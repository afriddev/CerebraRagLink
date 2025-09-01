from abc import ABC, abstractmethod
from ragservices.models import ExtarctQuestionAndAnswersFromDocResponse_Rag,HandleQaRagBuildingProcessResponseModel_Rag
from aiservices import EmbeddingResponseModel


class BuildQaRagFromDocImpl_Rag(ABC):

    @abstractmethod
    def ExtarctQuesionAndAnsersFromDocText_Rag(
        self, text: str
    ) -> ExtarctQuestionAndAnswersFromDocResponse_Rag:
        pass

    @abstractmethod
    async def ConvertTextsToVectorsFrom_Rag(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        pass

    @abstractmethod
    async def HandleQaRagBuildingProcess_Rag(self, docPath: str) -> HandleQaRagBuildingProcessResponseModel_Rag:
        pass
