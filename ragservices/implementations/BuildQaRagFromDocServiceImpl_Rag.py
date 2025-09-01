from abc import ABC, abstractmethod
from ragservices.models import ExtarctQuestionAndAnswersFromDocResponse_Rag


class BuildQaRagFromDocImpl_Rag(ABC):

    @abstractmethod
    def ExtarctQuesionAndAnsersFromDocText_Rag(
        self, text: str
    ) -> ExtarctQuestionAndAnswersFromDocResponse_Rag:
        pass

    @abstractmethod
    async def HandleQaRagBuildingProcess_Rag(self, docPath: str):
        pass
