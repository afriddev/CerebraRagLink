from pydantic import BaseModel
from server.enums import (
    ResponseEnum_Server,
    ChatServicePreProcessEnums_Server,
    ChatServicePreProcessRouteEnums_Server,
)


class ChatServiceRequestModel_Server(BaseModel):
    id: str | None = None
    query: str


class ChatServicePreProcessUserQueryResponseModel_Server(BaseModel):
    status: ChatServicePreProcessEnums_Server = (
        ChatServicePreProcessEnums_Server.OK
    )
    route: ChatServicePreProcessRouteEnums_Server = (
        ChatServicePreProcessRouteEnums_Server.LLM
    )


class ChatServiceResponseModel_Server(BaseModel):
    status: ResponseEnum_Server = ResponseEnum_Server.SUCCESS
    content: str | None = None
