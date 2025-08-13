from abc import ABC, abstractmethod

from models.LLMModels import LLMChatModel, LLMChatResponseModel


class LLMImpl(ABC):

    @abstractmethod
    async def Chat(self, modelParams: LLMChatModel) -> LLMChatResponseModel:
        pass

    @abstractmethod
    def HandleApiStatusError(self, statusCode: int) -> LLMChatResponseModel:
        pass
