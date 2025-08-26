from pydantic import BaseModel
from uuid import UUID


class EmbeddingTextModel(BaseModel):
    id: UUID
    vectorId: UUID
    question: str
    answer: str
    embeddingText: str


class EmbeddingVectorModel(BaseModel):
    id: UUID
    embeddingId: UUID
    embeddingVector: list[float]


class QaRagAskRequestModel(BaseModel):
    query: str