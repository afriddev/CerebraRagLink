from pydantic import BaseModel

from clientservices.mistral.enums import EmbeddingResponseEnum


class EmbeddingUsageModel(BaseModel):
    promptTokens: int | None
    completionTokens: int | None
    totalTokens: int | None


class EmbeddingDataModel(BaseModel):
    index: int | None
    embedding: list[float] | None




class EmbeddingResponseModel(BaseModel):
    status: EmbeddingResponseEnum = (
        EmbeddingResponseEnum.VALIDATION_ERROR
    )
    id: str | None = None
    model: str  | None = None
    usage: EmbeddingUsageModel | None = None
    data: list[EmbeddingDataModel] | None = None
