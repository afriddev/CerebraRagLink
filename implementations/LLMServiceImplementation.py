from abc import ABC, abstractmethod

from models import LLMChatModel, LLMChatResponseModel


class LLMServiceImpl(ABC):

    @abstractmethod
    async def Chat(self, modelParams: LLMChatModel) -> LLMChatResponseModel:
        pass

    @abstractmethod
    def HandleApiStatusError(self, statusCode: int) -> LLMChatResponseModel:
        pass
