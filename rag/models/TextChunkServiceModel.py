from uuid import UUID
from pydantic import BaseModel
from rag.enums import LLMChatResponseStatusEnum,ConvertTextToEmbeddingResponseErrorEnums


class TextChunkServiceQuestionAndAnswerForRagModel(BaseModel):
    question: str
    answer: str
    embeddingText: str


class ExtractQuestionAndAnswersVectorModel(BaseModel):
    embeddingVector: list[float]
    id: UUID
    embeddingId: UUID


class ExtarctQuestionAndAnswersFromTextForRagResponseModel(BaseModel):
    response: list[TextChunkServiceQuestionAndAnswerForRagModel] | None = None
    status: LLMChatResponseStatusEnum


class ExtractQuestionAndAnswersResponseModel(BaseModel):
    response: list[TextChunkServiceQuestionAndAnswerForRagModel] | None = None
    status: LLMChatResponseStatusEnum


class TextChunkServiceQuestionAndAnswerWithIdModel(
    TextChunkServiceQuestionAndAnswerForRagModel
):
    id: UUID
    vectorid: UUID 


class HandleQuestionAndAnswersProcessForRagResponseModel(BaseModel):
    questionAndAnsers: list[TextChunkServiceQuestionAndAnswerWithIdModel] | None = None
    status: LLMChatResponseStatusEnum | ConvertTextToEmbeddingResponseErrorEnums
    vectors:list[ExtractQuestionAndAnswersVectorModel] | None = None

