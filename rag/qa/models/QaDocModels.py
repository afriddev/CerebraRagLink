from uuid import UUID
from pydantic import BaseModel

from clientservices import (
    LLMResponseEnum,
    EmbeddingResponseEnum,
)


class ExtractQaEmbeddingTextModel(BaseModel):
    question: str
    answer: str
    embeddingText: str


class ExtractQaVectorModel(BaseModel):
    embeddingVector: list[float]
    id: UUID
    embeddingId: UUID


class ExtarctQaFromTextResponseModel(BaseModel):
    response: list[ExtractQaEmbeddingTextModel] | None = None
    status: LLMResponseEnum


class ExtractQaResponseModel(BaseModel):
    response: list[ExtractQaEmbeddingTextModel] | None = None
    status: LLMResponseEnum


class ExtractQaEmbeddingVectorModel(
    ExtractQaEmbeddingTextModel
):
    id: UUID
    vectorId: UUID


class HandleQaExtractResponseModel(BaseModel):
    questionAndAnsers: list[ExtractQaEmbeddingVectorModel] | None = None
    status: LLMResponseEnum | EmbeddingResponseEnum
    vectors: list[ExtractQaVectorModel] | None = None
