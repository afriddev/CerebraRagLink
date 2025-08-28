from typing import Any, List, Optional
from pydantic import BaseModel

from aiservices.chat.enums import (
    ChatServiceMessageRoleEnum,
    ChatServiceResponseStatusEnum,
)


class ChatServiceMessageModel(BaseModel):
    role: Optional[ChatServiceMessageRoleEnum] = ChatServiceMessageRoleEnum.USER
    content: str


class ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(BaseModel):
    type: str | int | float | str
    items: Optional[Any] = None
    properties: Optional[Any] = None
    required: Optional[Any] = None
    additionalProperties: Optional[Any] = None


class ChatServiceCerebrasFormatJsonSchemaJsonSchemaModel(BaseModel):
    type: str = "object"
    properties: dict[str, ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel] = {}
    required: List[str] = []
    additionalProperties: bool = False


class ChatServiceCerebrasFormatJsonSchemaModel(BaseModel):
    name: str = "schema"
    strict: bool = True
    jsonSchema: ChatServiceCerebrasFormatJsonSchemaJsonSchemaModel


class ChatServiceCerebrasFormatModel(BaseModel):
    type: str = "json_schema"
    jsonSchema: ChatServiceCerebrasFormatJsonSchemaModel


class ChatServiceRequestModel(BaseModel):
    model: str = "gpt-oss-120b"
    messages: List[ChatServiceMessageModel]
    maxCompletionTokens: Optional[int] = 20000
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    apiKey: str
    responseFormat: Optional[ChatServiceCerebrasFormatModel] = None
    topP:float = 1.0
    seed:int = 42
    


class ChatServiceChoiceMessageModel(BaseModel):
    role: ChatServiceMessageRoleEnum = ChatServiceMessageRoleEnum.ASSISTANT
    content: str


class ChatServiceChoiceModel(BaseModel):
    index: int = 0
    message: ChatServiceChoiceMessageModel


class ChatServiceUsageModel(BaseModel):
    promptTokens: int | None = None
    completionTokens: int | None = None
    totalTokens: int | None = None


class ChatServiceDataResponseModel(BaseModel):  
    id: str
    choices: List[ChatServiceChoiceModel] = []
    created: int
    model: str = "llama-3.3-70b"
    totalTime: float = 0.0
    usage: ChatServiceUsageModel


class ChatServiceResponseModel(BaseModel):
    status: ChatServiceResponseStatusEnum = ChatServiceResponseStatusEnum.SUCCESS
    LLMData: ChatServiceDataResponseModel | None = None
