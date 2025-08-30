from typing import Any
from server.serviceimplementations import GraphRagSearchServiceImpl_Server
import json


def GetEmbeddingService():
    from main import EmbeddingService

    return EmbeddingService


class GraphRagSearchService_Server(GraphRagSearchServiceImpl_Server):

    async def SearchOnDb_Server(self, query: str, db: Any):
        async with db.pool.acquire() as conn:
            await conn.set_type_codec(
                "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
            )

            embeddingService = await GetEmbeddingService().ConvertTextToEmbedding(
                text=[query]
            )
            queryVector = embeddingService.data[0].embedding

            sql = """  WITH q AS (
  SELECT $1::vector v
),
ids AS (
  -- main chunks
  SELECT c.id chunk_id, 1 - (c.text_vector <=> q.v) AS score
  FROM grag.chunks c, q
  UNION ALL
  SELECT cq.chunk_id, 1 - (cq.question_vector <=> q.v)
  FROM grag.chunk_questions cq, q
  UNION ALL
  SELECT cr.chunk_id, 1 - (cr.relation_vector <=> q.v)
  FROM grag.chunk_relations cr, q
),
base AS (
  SELECT DISTINCT i.chunk_id, i.score
  FROM ids i
),
-- add matched nodes if score >= 0.9
with_matched AS (
  SELECT b.chunk_id, b.score
  FROM base b
  UNION ALL
  SELECT mn.matched_chunk_id AS chunk_id, mn.score
  FROM grag.chunk_matched_nodes mn
  JOIN base b ON b.chunk_id = mn.chunk_id
  WHERE mn.score >= 0.9
)
SELECT c.id, c.text,
       COALESCE(
         jsonb_agg(DISTINCT jsonb_build_object('url', ci.image_url, 'description', ci.description))
         FILTER (WHERE ci.image_url IS NOT NULL),
         '[]'::jsonb
       ) AS images,
       MAX(w.score) AS best_score
FROM grag.chunks c
JOIN with_matched w ON w.chunk_id = c.id
LEFT JOIN grag.chunk_images ci ON ci.chunk_id = c.id
GROUP BY c.id, c.text
ORDER BY best_score DESC
LIMIT COALESCE($2::int, 100);
"""

            rows = await conn.fetch(sql, queryVector, 50)

        # Build response
        out = []
        for r in rows:
            text = r["text"]
            imgs = r["images"] or []
            if imgs:
                for img in imgs:
                    url = img.get("url")
                    desc = img.get("description") or ""
                    out.append(f"{text}\nImage: {url}\nThis image helps = {desc}")
            else:
                out.append(text)

        return out
