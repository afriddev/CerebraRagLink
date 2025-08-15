from pydantic import BaseModel
from rag.enums import LLMChatResponseStatusEnum

class TextChunkServiceQuestionAndAnswerForRagModel(BaseModel):

    question: str
    answer: str
    embeddingText: str


class ExtarctQuestionAndAnswersFromTextForRagResponseModel(BaseModel):
    response: list[TextChunkServiceQuestionAndAnswerForRagModel] | None = None
    status:LLMChatResponseStatusEnum 


class ExtractQuestionAndAnswersResponseModel(BaseModel):
    response: list[TextChunkServiceQuestionAndAnswerForRagModel] | None = None
    status: LLMChatResponseStatusEnum