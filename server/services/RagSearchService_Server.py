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
                WITH q AS (
                SELECT $1::vector v
                )
                SELECT qs.question_text AS "matchedText",
                    ans.answer AS "contextText",
                    1 - (qs.question_vector <=> q.v) AS score
                FROM qa.questions qs
                JOIN qa.answers ans ON qs.answer_id = ans.id
                JOIN q ON true
                ORDER BY qs.question_vector <-> q.v
                LIMIT $2;
                """

            rows = await conn.fetch(sql, queryVector, 20)

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
