from typing import Any
from server.serviceimplementations import RagSearchServiceImpl_Server
import json
from server.models import (
    SearchOnDbImageModel_Server,
    SearchOnDbResponseModel,
    SearchOnDbDocModel_Server,
)
from config.PsqlDbConfig import psqlDb
from aiservices import EmbeddingService


EmbeddingService_Rag = EmbeddingService()


class RagSearchService_Server(RagSearchServiceImpl_Server):

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
SELECT qs.text AS "matchedText",
       ck.text AS "contextText",
       COALESCE(
         (json_agg(
           json_build_object('url', im.image_url, 'description', im.description)
         ) FILTER (WHERE im.id IS NOT NULL))::jsonb,
         '[]'::jsonb
       ) AS images,
       qs.embedding <-> $1::vector AS dist
FROM ragmaster.userman_ck_questions qs
JOIN ragmaster.userman_cks ck ON qs.chunk_id = ck.id
LEFT JOIN ragmaster.userman_ck_images im ON im.chunk_id = ck.id
GROUP BY qs.id, ck.id

UNION ALL

SELECT rl.text AS "matchedText",
       ck.text AS "contextText",
       COALESCE(
         (json_agg(
           json_build_object('url', im.image_url, 'description', im.description)
         ) FILTER (WHERE im.id IS NOT NULL))::jsonb,
         '[]'::jsonb
       ) AS images,
       rl.embedding <-> $1::vector AS dist
FROM ragmaster.userman_ck_relations rl
JOIN ragmaster.userman_cks ck ON rl.chunk_id = ck.id
LEFT JOIN ragmaster.userman_ck_images im ON im.chunk_id = ck.id
GROUP BY rl.id, ck.id

UNION ALL

SELECT ck.text AS "matchedText",
       ck.text AS "contextText",
       COALESCE(
         (json_agg(
           json_build_object('url', im.image_url, 'description', im.description)
         ) FILTER (WHERE im.id IS NOT NULL))::jsonb,
         '[]'::jsonb
       ) AS images,
       ck.embedding <-> $1::vector AS dist
FROM ragmaster.userman_cks ck
LEFT JOIN ragmaster.userman_ck_images im ON im.chunk_id = ck.id
GROUP BY ck.id

UNION ALL

SELECT qq.text AS "matchedText",
       ans.text AS "contextText",
       '[]'::jsonb AS images,
       qq.embedding <-> $1::vector AS dist
FROM ragmaster.qa_ques qq
JOIN ragmaster.qa_answers ans ON qq.answer_id = ans.id

ORDER BY dist
LIMIT $2;


                """

            rows = await conn.fetch(sql, queryVector, 100)

        docs: list[SearchOnDbDocModel_Server] = []

        for r in rows:
            matchedText = r["matchedText"]
            contextText = r["contextText"]
            imgs: Any = []

            try:
                imgs = r["images"]
            except:
                imgs = []

            images: list[SearchOnDbImageModel_Server] = []

            if imgs:
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

            docs.append(
                SearchOnDbDocModel_Server(
                    matchedText=matchedText, contextText=contextText, images=images
                )
            )

        return SearchOnDbResponseModel(docs=docs)
