from typing import Any
from server.serviceimplementations import BuildGraphRagFromDocServiceImpl_Server
from ragservices import BuildGraphFromDocService_Rag, GetGraphFromDocResponseModel_Rag

BuildGraphRagFromDocService = BuildGraphFromDocService_Rag()


class BuildGraphRagFromDocService_Server(BuildGraphRagFromDocServiceImpl_Server):

    async def BuildGraphFromDoc(self, file: str, db: Any):
        conn = await db.get_connection()

        graph: GetGraphFromDocResponseModel_Rag = (
            await BuildGraphRagFromDocService.BuildGraphFromDoc_Rag(file)
        )

        chunkTexts: list[Any] = []
        chunkQuestions: list[Any] = []
        chunkImages: list[Any] = []

        for ct in graph.chunkTexts:
            chunkTexts.append((ct.id, ct.text, ct.vector, ct.entities))

            for i, q in enumerate(ct.questions):
                try:
                    chunkQuestions.append((ct.id, q, ct.questionVectors[i]))
                except Exception as ex:
                    print(f"Error processing question for chunk {ct.id}: {q}")
                    print(ex)


            for img in ct.images or []:
                chunkImages.append(
                    (
                        ct.id,
                        img.sectionNumber,
                        img.title,
                        img.image,
                        img.description,
                    )
                )

        await conn.executemany(
            """
            INSERT INTO grag.chunks (id, text, text_vector, entities)
            VALUES ($1, $2, $3, $4)
            """,
            chunkTexts,
        )

        await conn.executemany(
            """
            INSERT INTO grag.chunk_questions (chunk_id, question_text, question_vector)
            VALUES ($1, $2, $3)
            """,
            chunkQuestions,
        )

        await conn.executemany(
            """
            INSERT INTO grag.chunk_images (chunk_id, section_number, title, image_url, description)
            VALUES ($1, $2, $3, $4, $5)
            """,
            chunkImages,
        )

        chunkRelations: list[Any] = []
        for cr in graph.chunkRelations:
            for rel in cr.chunkRelations:
                chunkRelations.append(
                    (
                        cr.chunkId,
                        rel.realtion,
                        rel.relationVector,
                        rel.realtionEntites,
                    )
                )

        await conn.executemany(
            """
            INSERT INTO grag.chunk_relations (chunk_id, relation, relation_vector, relation_entities)
            VALUES ($1, $2, $3, $4)
            """,
            chunkRelations,
        )
