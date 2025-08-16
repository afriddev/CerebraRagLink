from pydantic import BaseModel
from clientservices import LLMResponseEnum


class QaAiAnswersRequestModel(BaseModel):
    ragResponseText: str
    query: str


class QaAiAnswersResponseModel(BaseModel):
    status: LLMResponseEnum
    response: str | None
