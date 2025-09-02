from typing import Any, cast
from server.serviceimplementations import BuildRagFromDocServiceImpl_Server
from ragservices import (
    BuildRagFromDocService_Rag,
    GetRagFromDocResponseModel_Rag,
    BuildQaRagFromDocService_Rag,
    HandleQaRagBuildingProcessResponseModel_Rag,
)
from config.PsqlDbConfig import psqlDb
from uuid import uuid4, UUID

BuildGraphRagFromDocService = BuildRagFromDocService_Rag()
BuildQaRagFromDocService = BuildQaRagFromDocService_Rag()


class BuildRagFromDocService_Server(BuildRagFromDocServiceImpl_Server):

    async def BuildQaRagFromDoc(self, file: str):
        qa: HandleQaRagBuildingProcessResponseModel_Rag = (
            await BuildQaRagFromDocService.HandleQaRagBuildingProcess_Rag(docPath=file)
        )

        questions: Any = []
        answers: Any = []

        for i, _ in enumerate(qa.questions):
            answerId: UUID = uuid4()
            answers.append((answerId, qa.answers[i]))
            questions.append((answerId, qa.questions[i], qa.questionVectors[i]))

        try:
            async with psqlDb.pool.acquire() as conn:
                await conn.executemany(
                    "INSERT INTO ragmaster.qa_answers (id, text) VALUES ($1, $2)",
                    answers,
                )

                await conn.executemany(
                    "INSERT INTO ragmaster.qa_ques (answer_id,text,embedding) VALUES ($1, $2, $3)",
                    questions,
                )
        except Exception as e:
            print(e)

    async def BuildRagFromDoc(self, file: str):
        graph: GetRagFromDocResponseModel_Rag = (
            await BuildGraphRagFromDocService.BuildRagFromDoc_Rag(file)
        )

        chunkTexts: list[Any] = []
        chunkQuestions: list[Any] = []
        chunkImages: list[Any] = []
        chunkRelations: list[Any] = []

        for ct in graph.chunkTexts:
            chunkTexts.append((ct.id, ct.text, ct.vector))
            for i, q in enumerate(ct.questions):
                chunkQuestions.append((ct.id, q, cast(Any, ct).questionVectors[i]))
            for img in ct.images or []:
                chunkImages.append((ct.id, img.image, img.description))

        for cr in graph.chunkRelations:
            for rel in cr.chunkRelations:
                chunkRelations.append((cr.chunkId, rel.realtion, rel.relationVector))

        async with psqlDb.pool.acquire() as conn:
            if chunkTexts:
                await conn.executemany(
                    "INSERT INTO ragmaster.userman_cks (id, text, embedding) VALUES ($1, $2, $3)",
                    chunkTexts,
                )
            if chunkQuestions:
                await conn.executemany(
                    "INSERT INTO ragmaster.userman_ck_questions (chunk_id, text, embedding) VALUES ($1, $2, $3)",
                    chunkQuestions,
                )
            if chunkImages:
                await conn.executemany(
                    "INSERT INTO ragmaster.userman_ck_images (chunk_id, image_url, description) VALUES ($1, $2, $3)",
                    chunkImages,
                )
            if chunkRelations:
                await conn.executemany(
                    "INSERT INTO ragmaster.userman_ck_relations (chunk_id, text, embedding) VALUES ($1, $2, $3)",
                    chunkRelations,
                )
