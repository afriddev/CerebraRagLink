from typing import Any
from fastapi.responses import JSONResponse
from server.implementations import QaRagContollerImpl
from rag import TextChunkService
from clientservices import EmbeddingService
from server.models import EmbeddingVectorModel, EmbeddingTextModel


class QaRagControllerServices(QaRagContollerImpl):
    async def QaRagExtract(self, db: Any) -> JSONResponse:
        textChunkService = TextChunkService()
        result = await textChunkService.HandleQaExtract("a.pdf")
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
        VALUES ($1, $2, $3::vector)
    """,
            [
                (
                    ev.id,
                    ev.embeddingId,
                    ev.embeddingVector,
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
        embedding: list[float] = vectorResponse.data[0].embedding
        conn = await db.get_connection()
        sql = """
        SELECT t.id, t.vector_id, t.question, t.answer, t.embedding_text,
            (v.embedding_vector <-> $1) AS distance
        FROM qa_embedding_texts t
        JOIN qa_embedding_vectors v
        ON t.vector_id = v.id
        ORDER BY distance
        LIMIT 5;
        """
        rows = await conn.fetch(sql, embedding)
        await db.release_connection(conn)
        results = []
        for r in rows:
            row_dict = dict(r)
            # Convert UUIDs to str
            if "id" in row_dict and row_dict["id"] is not None:
                row_dict["id"] = str(row_dict["id"])
            if "vector_id" in row_dict and row_dict["vector_id"] is not None:
                row_dict["vector_id"] = str(row_dict["vector_id"])
            results.append(row_dict)
        return JSONResponse(
            status_code=200,
            content={
                "message": "Ask endpoint executed successfully",
                "results": results,
            },
        )
