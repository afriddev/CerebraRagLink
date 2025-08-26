from typing import Any
from pydantic import BaseModel
from clientservices.embedding.enums import (
    MistralChatMessageRoleEnum,
    MistralChatResponseStatusEnum
)


class MistralChatRequestMessageModel(BaseModel):
    role: MistralChatMessageRoleEnum = MistralChatMessageRoleEnum.USER
    content: str | list[str]


class MistralChatRequestModel(BaseModel):
    model: str = "mistral-small-2506"
    temperature: float = 0.7
    maxTokens: int = 30000
    stream: bool = False
    messages: list[MistralChatRequestMessageModel]
    responseFormat: Any | None = None


class MistralChatResponseUsageModel(BaseModel):
    promptTokens: int
    completionToken: int
    totalTokens: int


class MistralChatResponseMessageModel(BaseModel):
    content: str
    role: str | None = None


class MistralChatResponseChoiceModel(BaseModel):
    index: int
    message: MistralChatResponseMessageModel


class MistralChatResponseModel(BaseModel):
    id: str | None = None
    model: str | None = None
    usgae: MistralChatResponseUsageModel | None = None
    created: int | None = None
    choices: list[MistralChatResponseChoiceModel] | None = None
    status:MistralChatResponseStatusEnum