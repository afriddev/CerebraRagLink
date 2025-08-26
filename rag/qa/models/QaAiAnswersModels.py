from pydantic import BaseModel
from clientservices import ChatServiceResponseStatusEnum


class QaAiAnswersRequestModel(BaseModel):
    ragResponseText: str
    query: str


class QaAiAnswersResponseModel(BaseModel):
    status: ChatServiceResponseStatusEnum
    response: str | None
