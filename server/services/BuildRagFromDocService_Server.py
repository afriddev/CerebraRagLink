from typing import Any, cast
from server.serviceimplementations import BuildRagFromDocServiceImpl_Server
from ragservices import (
    BuildGraphFromDocService_Rag,
    GetGraphFromDocResponseModel_Rag,
    BuildQaRagFromDocService_Rag,
    HandleQaRagBuildingProcessResponseModel_Rag,
)
from config.PsqlDbConfig import psqlDb
from uuid import uuid4, UUID

BuildGraphRagFromDocService = BuildGraphFromDocService_Rag()
BuildQaRagFromDocService = BuildQaRagFromDocService_Rag()


class BuildRagFromDocService_Server(BuildRagFromDocServiceImpl_Server):

    async def BuildRagFromDoc(self, file: str):
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
                    "INSERT INTO qa.answers (id, answer) VALUES ($1, $2)",
                    answers,
                )

                await conn.executemany(
                    "INSERT INTO qa.questions (answer_id,question_text,question_vector) VALUES ($1, $2, $3)",
                    answers,
                )
        except Exception as e:
            print(e)

    async def BuildGraphRagFromDoc(self, file: str):
        graph: GetGraphFromDocResponseModel_Rag = (
            await BuildGraphRagFromDocService.BuildGraphFromDoc_Rag(file)
        )

        chunkTexts: list[Any] = []
        chunkQuestions: list[Any] = []
        chunkImages: list[Any] = []
        chunkRelations: list[Any] = []
        chunkMatchedNodes: list[Any] = []

        for ct in graph.chunkTexts:
            chunkTexts.append((ct.id, ct.text, ct.vector, ct.entities))
            for i, q in enumerate(ct.questions):
                chunkQuestions.append((ct.id, q, cast(Any, ct).questionVectors[i]))
            for img in ct.images or []:
                chunkImages.append((ct.id, img.image, img.description))
            for mn in ct.matchedNodes or []:
                chunkMatchedNodes.append((ct.id, mn.chunkId, mn.score))

        for cr in graph.chunkRelations:
            for rel in cr.chunkRelations:
                chunkRelations.append(
                    (cr.chunkId, rel.realtion, rel.relationVector, rel.realtionEntites)
                )

        async with psqlDb.pool.acquire() as conn:
            if chunkTexts:
                await conn.executemany(
                    "INSERT INTO grag.chunks (id, text, text_vector, entities) VALUES ($1, $2, $3, $4)",
                    chunkTexts,
                )
            if chunkMatchedNodes:
                await conn.executemany(
                    "INSERT INTO grag.chunk_matched_nodes (chunk_id, matched_chunk_id, score) VALUES ($1, $2, $3)",
                    chunkMatchedNodes,
                )
            if chunkQuestions:
                await conn.executemany(
                    "INSERT INTO grag.chunk_questions (chunk_id, question_text, question_vector) VALUES ($1, $2, $3)",
                    chunkQuestions,
                )
            if chunkImages:
                await conn.executemany(
                    "INSERT INTO grag.chunk_images (chunk_id, image_url, description) VALUES ($1, $2, $3)",
                    chunkImages,
                )
            if chunkRelations:
                await conn.executemany(
                    "INSERT INTO grag.chunk_relations (chunk_id, relation, relation_vector, relation_entities) VALUES ($1, $2, $3, $4)",
                    chunkRelations,
                )
