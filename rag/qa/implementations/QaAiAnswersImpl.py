from abc import ABC, abstractmethod
from rag.qa.models import QaAiAnswersResponseModel, QaAiAnswersRequestModel


class QaAiAnswersImpl(ABC):

    @abstractmethod
    async def QaResponse(
        self,
        request: QaAiAnswersRequestModel,
    ) -> QaAiAnswersResponseModel:
        pass
