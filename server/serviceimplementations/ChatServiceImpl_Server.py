from abc import ABC, abstractmethod

from fastapi.responses import StreamingResponse
from server.models import (
    ChatServiceResponseModel_Server,
    ChatServiceRequestModel_Server,
    ChatServicePreProcessUserQueryResponseModel_Server,
)
from aiservices import ChatServiceMessageModel


class ChatServiceImpl_Server(ABC):

    @abstractmethod
    async def HandlePreProcessUserQuery_Server(
        self, query: str, messages: list[ChatServiceMessageModel], loopIndex: int
    ) -> ChatServicePreProcessUserQueryResponseModel_Server:
        pass

    @abstractmethod
    async def LLMChat_Server(
        self, messages: list[ChatServiceMessageModel]
    ) -> StreamingResponse | None:
        pass

    @abstractmethod
    async def ChatService_Server(
        self, request: ChatServiceRequestModel_Server
    ) -> StreamingResponse:
        pass
