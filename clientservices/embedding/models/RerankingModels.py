from pydantic import BaseModel
from clientservices.chat.enums import ChatServiceResponseStatusEnum


class RerankingRequestModel(BaseModel):
    model: str = "Salesforce/Llama-Rank-v1"
    query: str
    docs: list[str]
    topN: int = 5


class RerankingResponseChoiseModel(BaseModel):
    index: int
    score: float


class RerankingUsageModel(BaseModel):
    totalTokens: int


class RerankingResponseModel(BaseModel):
    response: list[RerankingResponseChoiseModel] | None = None
    status: ChatServiceResponseStatusEnum = ChatServiceResponseStatusEnum.SUCCESS
    usage: RerankingUsageModel | None = None
