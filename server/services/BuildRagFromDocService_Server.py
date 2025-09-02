from typing import Any, cast
from server.serviceimplementations import BuildRagFromDocServiceImpl_Server
from ragservices import BuildRagFromDoc, BuildQaRagFromDoc, BuildRagFromDocResponseModel
from config.PsqlDbConfig import psqlDb
from uuid import uuid4, UUID

BuildRag = BuildRagFromDoc()

BuildQaRag = BuildQaRagFromDoc()


class BuildRagFromDocService_Server(BuildRagFromDocServiceImpl_Server):

    async def BuildQaRagFromDoc(self, file: str):
        qa: BuildRagFromDocResponseModel = await BuildRag.BuildRagFromDoc(file=file)

        questions: Any = []
        answers: Any = []

        for i, _ in enumerate(qa.chunkQuestion):
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
        chunkRelations: list[Any] = []

        for ct in graph.chunkTexts:
            chunkTexts.append((ct.id, ct.text, ct.vector))
            for i, q in enumerate(ct.questions):
                chunkQuestions.append((ct.id, q, cast(Any, ct).questionVectors[i]))

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
            if chunkRelations:
                await conn.executemany(
                    "INSERT INTO ragmaster.userman_ck_relations (chunk_id, text, embedding) VALUES ($1, $2, $3)",
                    chunkRelations,
                )
