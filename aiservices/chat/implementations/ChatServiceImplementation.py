from abc import ABC, abstractmethod

from fastapi.responses import StreamingResponse

from aiservices.chat.models import ChatServiceRequestModel, ChatServiceResponseModel


class ChatServiceImpl(ABC):

    @abstractmethod
    async def Chat(self, modelParams: ChatServiceRequestModel) -> ChatServiceResponseModel | StreamingResponse:
        pass

    @abstractmethod
    def HandleApiStatusError(
        self, statusCode: int
    ) -> ChatServiceResponseModel :
        pass
