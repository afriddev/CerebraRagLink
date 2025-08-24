from uuid import UUID
from pydantic import BaseModel

from clientservices import (
    ChatServiceResponseStatusEnum,
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
    status: ChatServiceResponseStatusEnum


class ExtractQaResponseModel(BaseModel):
    response: list[ExtractQaEmbeddingTextModel] | None = None
    status: ChatServiceResponseStatusEnum


class ExtractQaEmbeddingVectorModel(
    ExtractQaEmbeddingTextModel
):
    id: UUID
    vectorId: UUID


class HandleQaExtractResponseModel(BaseModel):
    questionAndAnsers: list[ExtractQaEmbeddingVectorModel] | None = None
    status: ChatServiceResponseStatusEnum | EmbeddingResponseEnum
    vectors: list[ExtractQaVectorModel] | None = None
