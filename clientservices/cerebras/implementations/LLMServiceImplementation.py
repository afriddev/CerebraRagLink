from abc import ABC, abstractmethod

from clientservices.cerebras.models import LLMRequestModel, LLMResponseModel


class LLMServiceImpl(ABC):

    @abstractmethod
    async def Chat(self, modelParams: LLMRequestModel) -> LLMResponseModel:
        pass

    @abstractmethod
    def HandleApiStatusError(self, statusCode: int) -> LLMResponseModel:
        pass
