from pydantic import BaseModel

from rag.enums import ConvertTextToEmbeddingResponseErrorEnums


class ConvertTextToEmbeddingResponseUsageModel(BaseModel):
    promptTokens: int | None
    completionTokens: int | None
    totalTokens: int | None


class ConvertTextToEmbeddingResponseDataModel(BaseModel):
    index: int | None
    embedding: list[float] | None


class ConvertTextToEmbeddingResponseModel(BaseModel):
    id: str
    model: str = "mistral-embed"
    usage: ConvertTextToEmbeddingResponseUsageModel
    data: list[ConvertTextToEmbeddingResponseDataModel]


class ConvertTextToEmbeddingResponseErrorModel(BaseModel):
    status: ConvertTextToEmbeddingResponseErrorEnums = (
        ConvertTextToEmbeddingResponseErrorEnums.VALIDATION_ERROR
    )
