from typing import Any
from server.serviceimplementations import GraphRagSearchServiceImpl_Server
import json


def GetEmbeddingService():
    from main import EmbeddingService

    return EmbeddingService


class GraphRagSearchService_Server(GraphRagSearchServiceImpl_Server):


    async def SearchOnDb_Server(self, query: str, db: Any):
        conn = await db.get_connection()

        # make jsonb fields come back as Python dict/list instead of str
        await conn.set_type_codec('jsonb', encoder=json.dumps, decoder=json.loads, schema='pg_catalog')

        embeddingService = await GetEmbeddingService().ConvertTextToEmbedding(text=[query])
        queryVector = embeddingService.data[0].embedding
        print(queryVector)
        sql = """
        WITH q AS (SELECT $1::vector v), ids AS (
        SELECT c.id chunk_id,1-(c.text_vector<=>q.v) score FROM grag.chunks c,q
        UNION ALL SELECT cq.chunk_id,1-(cq.question_vector<=>q.v) FROM grag.chunk_questions cq,q
        UNION ALL SELECT cr.chunk_id,1-(cr.relation_vector<=>q.v) FROM grag.chunk_relations cr,q
        )
        SELECT c.id, c.text,
            COALESCE(
                jsonb_agg(DISTINCT jsonb_build_object('url',ci.image_url,'description',ci.description))
                FILTER (WHERE ci.image_url IS NOT NULL),
                '[]'::jsonb
            ) AS images
        FROM grag.chunks c
        LEFT JOIN grag.chunk_images ci ON ci.chunk_id=c.id
        WHERE c.id IN (SELECT chunk_id FROM ids)
        GROUP BY c.id,c.text
        ORDER BY (SELECT MAX(score) FROM ids i WHERE i.chunk_id=c.id) DESC
        LIMIT COALESCE($2::int,100);
        """

        try:
            rows = await conn.fetch(sql, queryVector, 50)
        finally:
            await conn.close()

        # Build list[str]: "text\nImage: <url>\nThis image helps = <description>"
        out = []
        for r in rows:
            text = r["text"]
            imgs = r["images"]  # now a Python list
            if imgs:
                for img in imgs:
                    url = img.get("url")
                    desc = img.get("description") or ""
                    out.append(f"{text}\nImage: {url}\nThis image helps = {desc}")
            else:
                out.append(text)
        print(out)
        return out
