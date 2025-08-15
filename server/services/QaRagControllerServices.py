from typing import Any

from fastapi.responses import JSONResponse
from server.implementations import QaRagContollerImpl

from rag import TextChunkService, EmbeddingService
from server.models import EmbeddingVectorModel, EmbeddingTextModel


class QaRagControllerServices(QaRagContollerImpl):

    async def QaRagExtarct(self, db: Any) -> JSONResponse:
        textChunkService = TextChunkService()
        result = await textChunkService.HandleQuestionAndAnswersProcessForRag("a.pdf")
        embeddingTexts: list[EmbeddingTextModel] = []
        embeddingVectors: list[EmbeddingVectorModel] = []

        if result.questionAndAnsers is not None and result.vectors is not None:
            for qa, vec in zip(result.questionAndAnsers, result.vectors):
                embeddingTexts.append(
                    EmbeddingTextModel(
                        vectorId=qa.vectorId,
                        question=qa.question,
                        answer=qa.answer,
                        embeddingText=qa.embeddingText,
                        id=qa.id,
                    )
                )
                embeddingVectors.append(
                    EmbeddingVectorModel(
                        embeddingId=vec.embeddingId,
                        embeddingVector=vec.embeddingVector,
                        id=vec.id,
                    )
                )
        conn = await db.get_connection()
        await conn.executemany(
            """
        INSERT INTO qa_embedding_texts (id, vector_id, question, answer, embedding_text)
        VALUES ($1, $2, $3, $4, $5)
    """,
            [
                (et.id, et.vectorId, et.question, et.answer, et.embeddingText)
                for et in embeddingTexts
            ],
        )

        await conn.executemany(
            """
        INSERT INTO qa_embedding_vectors (id, embedding_id, embedding_vector)
        VALUES ($1, $2, $3)
    """,
            [
                (
                    ev.id,
                    ev.embeddingId,
                    "[" + ", ".join(map(str, ev.embeddingVector)) + "]",
                )
                for ev in embeddingVectors
            ],
        )

        await db.release_connection(conn)

        return JSONResponse(
            status_code=result.status.value[0], content={"data": result.status.value[1]}
        )

    async def QaRagAsk(self, query: str, db: Any) -> JSONResponse:
        vectorResponse = await EmbeddingService().ConvertTextToEmbedding(text=[query])

        return JSONResponse(
            status_code=200, content={"message": "Ask endpoint is not implemented yet."}
        )
