from pydantic import BaseModel


class ExtarctQuestionAndAnswersFromDocResponse_Rag(BaseModel):
    questions: list[str]
    response: list[str]
