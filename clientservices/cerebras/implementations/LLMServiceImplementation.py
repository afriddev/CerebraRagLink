from abc import ABC, abstractmethod

from fastapi.responses import StreamingResponse

from clientservices.cerebras.models import LLMRequestModel, LLMResponseModel


class LLMServiceImpl(ABC):

    @abstractmethod
    async def Chat(self, modelParams: LLMRequestModel) -> LLMResponseModel | StreamingResponse:
        pass

    @abstractmethod
    def HandleApiStatusError(
        self, statusCode: int
    ) -> LLMResponseModel :
        pass
