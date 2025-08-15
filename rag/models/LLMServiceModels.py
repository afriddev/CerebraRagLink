from typing import Any, List, Optional
from pydantic import BaseModel
from rag.enums import (
    LLMChatMessageRoleEnum,
    LLMChatResponseStatusEnum,
)


class LLMChatMessageModel(BaseModel):
    role: Optional[LLMChatMessageRoleEnum] = LLMChatMessageRoleEnum.USER
    content: str


class LLMChatResponsePropertySchemaModel(BaseModel):
    type: str | int | float | str
    items: Optional[Any] = None


class LLMChatResponseFormatJsonSchemaSchemaModel(BaseModel):
    type: str = "object"
    properties: dict[str, LLMChatResponsePropertySchemaModel] = {}
    required: List[str] = []
    additionalProperties: bool = False


class LLMChatResponseFormatJsonSchemaModel(BaseModel):
    name: str = "schema"
    strict: bool = True
    jsonSchema: LLMChatResponseFormatJsonSchemaSchemaModel


class LLMChatResponseFormatModel(BaseModel):
    type: str = "json_schema"
    jsonSchema: LLMChatResponseFormatJsonSchemaModel


class LLMChatModel(BaseModel):
    model: str = "llama-3.3-70b"
    messages: List[LLMChatMessageModel]
    maxCompletionTokens: Optional[int] = 20000
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    apiKey: str
    responseFormat: Optional[LLMChatResponseFormatModel] = None


class LLMChatDataChoiseMessageModel(BaseModel):
    role: LLMChatMessageRoleEnum = LLMChatMessageRoleEnum.ASSISTANT
    content: str


class LLMChatDataChoiseModel(BaseModel):
    index: int = 0
    message: LLMChatDataChoiseMessageModel


class LLMChatDataUsageModel(BaseModel):
    promptTokens: int | None = None
    completionTokens: int | None = None
    totalTokens: int | None = None


class LLMChatDataModel(BaseModel):
    id: str
    choices: List[LLMChatDataChoiseModel] = []
    created: int
    model: str = "llama-3.3-70b"
    totalTime: float = 0.0
    usage: LLMChatDataUsageModel


class LLMChatResponseModel(BaseModel):
    status: LLMChatResponseStatusEnum = LLMChatResponseStatusEnum.SUCCESS
    LLMData: LLMChatDataModel | None = None
