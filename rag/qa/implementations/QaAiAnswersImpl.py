from abc import ABC, abstractmethod

from fastapi.responses import StreamingResponse
from rag.qa.models import QaAiAnswersResponseModel, QaAiAnswersRequestModel


class QaAiAnswersImpl(ABC):

    @abstractmethod
    async def QaResponse(
        self,
        request: QaAiAnswersRequestModel,
    ) -> StreamingResponse:
        pass
