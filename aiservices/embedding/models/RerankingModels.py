from pydantic import BaseModel
from aiservices.chat.enums import ChatServiceResponseStatusEnum


class RerankingRequestModel(BaseModel):
    model: str = "jina-reranker-m0"
    query: str
    docs: list[str]
    topN: int = 5
    returnDocuments: bool = False


class RerankingResponseChoiseModel(BaseModel):
    index: int
    score: float


class RerankingUsageModel(BaseModel):
    totalTokens: int


class RerankingResponseModel(BaseModel):
    response: list[RerankingResponseChoiseModel] | None = None
    status: ChatServiceResponseStatusEnum = ChatServiceResponseStatusEnum.SUCCESS
    usage: RerankingUsageModel | None = None


class FindTopKresultsFromVectorsRequestModel(BaseModel):
    sourceVectors: list[list[float]]
    queryVector: list[float]
    topK: int = 20
    
class FindTopKresultsFromVectorsResponseModel(BaseModel):
    distances:list[float] | None = None
    indeces:list[int] | None = None