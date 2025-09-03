from typing import Any, cast
from server.implementations import BuildRagServiceImpl
from ragservices import (
    BuildRagFromDoc,
    BuildQaRagFromDoc,
    BuildRagFromDocResponseModel,
    BuildQaRagFromDocResponseModel,
)
from config.PsqlDbConfig import psqlDb
from uuid import uuid4

BuildRag = BuildRagFromDoc()

BuildQaRag = BuildQaRagFromDoc()


class BuildRagService(BuildRagServiceImpl):

    async def BuildRag(self, file: str):
        claimChunks: Any = []
        claims: Any = []
        qa: BuildQaRagFromDocResponseModel = await BuildQaRag.BuildQaRagFromDoc(
            file=file
        )

        for index, item in enumerate(qa.questions):
            claimChunkId = uuid4()
            claimChunks.append((claimChunkId, qa.answers[index]))
            claims.append((claimChunkId, item, qa.questionEmbeddings[index]))

        # rag: BuildRagFromDocResponseModel = await BuildRag.BuildRagFromDoc(file=file)

        # for _, item in enumerate(rag.chunkTexts):
        #     claimChunks.append((item.id, item.text))

        # for _, item in enumerate(rag.chunkClaims):
        #     for index1, claim in enumerate(item.claims):
        #         claims.append(
        #             (item.chunkId, claim, cast(Any, item).ClaimEmbeddings[index1])
        #         )

        # for _, item in enumerate(rag.chunkQuestion):
        #     for index1, question in enumerate(item.questions):
        #         claims.append(
        #             (item.chunkId, question, cast(Any, item).questionEmbeddings[index1])
        #         )

        try:
            async with psqlDb.pool.acquire() as conn:
                await conn.executemany(
                    "INSERT INTO ragmaster.claim_chunks (id, text) VALUES ($1, $2)",
                    claimChunks,
                )

                await conn.executemany(
                    "INSERT INTO ragmaster.claims (claim_chunk_id,text,embedding) VALUES ($1, $2, $3)",
                    claims,
                )
        except Exception as e:
            print(e)
