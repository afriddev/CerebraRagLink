from typing import Any
from server.serviceimplementations import GraphRagSearchServiceImpl_Server
import json
from server.models import (
    SearchOnDbImageModel_Server,
    SearchOnDbResponseModel,
    SearchOnDbDocModel_Server,
)
from config.PsqlDbConfig import psqlDb
from aiservices import EmbeddingService


EmbeddingService_Rag = EmbeddingService()


class GraphRagSearchService_Server(GraphRagSearchServiceImpl_Server):

    async def SearchOnDb_Server(self, query: str) -> SearchOnDbResponseModel:
        async with psqlDb.pool.acquire() as conn:
            await conn.set_type_codec(
                "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
            )

            embeddingService: Any = await EmbeddingService_Rag.ConvertTextToEmbedding(
                text=[query]
            )
            queryVector = embeddingService.data[0].embedding

            sql = """ 

            WITH q AS (
              SELECT $1::vector v
            ),
            ids AS (
              SELECT c.id AS chunk_id, 1 - (c.text_vector <=> q.v) AS score
              FROM grag.chunks c, q
              UNION ALL
              SELECT cq.chunk_id, 1 - (cq.question_vector <=> q.v)
              FROM grag.chunk_questions cq, q
              UNION ALL
              SELECT cr.chunk_id, 1 - (cr.relation_vector <=> q.v)
              FROM grag.chunk_relations cr, q
            ),
            base AS (
              SELECT i.chunk_id, MAX(i.score) AS score
              FROM ids i
              GROUP BY i.chunk_id
            ),
            with_matched AS (
              SELECT b.chunk_id, b.score
              FROM base b

              UNION ALL
              SELECT mn.matched_chunk_id AS chunk_id, mn.score
              FROM grag.chunk_matched_nodes mn
              JOIN base b ON b.chunk_id = mn.chunk_id
            )
            SELECT c.id,
                  c.text,
                  COALESCE(
                    jsonb_agg(
                      DISTINCT jsonb_build_object('url', ci.image_url, 'description', ci.description)
                    ) FILTER (WHERE ci.image_url IS NOT NULL),
                    '[]'::jsonb
                  ) AS images,
                  MAX(w.score) AS best_score
            FROM grag.chunks c
            JOIN with_matched w ON w.chunk_id = c.id
            LEFT JOIN grag.chunk_images ci ON ci.chunk_id = c.id
            GROUP BY c.id, c.text
            ORDER BY best_score DESC
            LIMIT $2;

"""

            rows = await conn.fetch(sql, queryVector, 50)

        docs: list[SearchOnDbDocModel_Server] = []

        for r in rows:
            text = r["text"]
            imgs: Any = r["images"] or []
            if imgs:
                images: list[SearchOnDbImageModel_Server] = []
                for img in imgs:
                    if (
                        img.get("url") != ""
                        and img.get("url") is not None
                        and img.get("description") != ""
                        and img.get("description") is not None
                    ):
                        url: str = img.get("url")
                        desc: str = img.get("description")
                        images.append(
                            SearchOnDbImageModel_Server(url=url, description=desc)
                        )

                docs.append(SearchOnDbDocModel_Server(doc=text, images=images))

        return SearchOnDbResponseModel(docs=docs)
