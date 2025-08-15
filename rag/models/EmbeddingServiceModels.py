from pydantic import BaseModel

from rag.enums import ConvertTextToEmbeddingResponseErrorEnums


class ConvertTextToEmbeddingResponseUsageModel(BaseModel):
    promptTokens: int | None
    completionTokens: int | None
    totalTokens: int | None


class ConvertTextToEmbeddingResponseDataModel(BaseModel):
    index: int | None
    embedding: list[float] | None




class ConvertTextToEmbeddingResponseErrorModel(BaseModel):
    status: ConvertTextToEmbeddingResponseErrorEnums = (
        ConvertTextToEmbeddingResponseErrorEnums.VALIDATION_ERROR
    )
    id: str | None = None
    model: str  | None = None
    usage: ConvertTextToEmbeddingResponseUsageModel | None = None
    data: list[ConvertTextToEmbeddingResponseDataModel] | None = None
