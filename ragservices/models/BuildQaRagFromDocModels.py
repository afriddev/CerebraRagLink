from pydantic import BaseModel


class ExtarctQaResponseModel(BaseModel):
    questions: list[str]
    answers: list[str]


class BuildQaRagFromDocResponseModel(
    ExtarctQaResponseModel
):
    questionEmbeddings: list[list[float]]
