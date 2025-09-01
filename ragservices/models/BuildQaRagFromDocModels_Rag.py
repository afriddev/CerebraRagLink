from pydantic import BaseModel


class ExtarctQuestionAndAnswersFromDocResponse_Rag(BaseModel):
    questions: list[str]
    answers: list[str]


class HandleQaRagBuildingProcessResponseModel_Rag(
    ExtarctQuestionAndAnswersFromDocResponse_Rag
):
    questionVectors: list[list[float]]
