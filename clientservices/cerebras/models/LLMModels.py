from typing import Any, List, Optional
from pydantic import BaseModel

from clientservices.cerebras.enums import (
    LLmMessageRoleEnum,
    LLMResponseEnum,
)


class LLmMessageModel(BaseModel):
    role: Optional[LLmMessageRoleEnum] = LLmMessageRoleEnum.USER
    content: str


class LLMResponseFormatPropertySchemaModel(BaseModel):
    type: str | int | float | str
    items: Optional[Any] = None


class LLMResponseFormatJsonSchemaSchemaModel(BaseModel):
    type: str = "object"
    properties: dict[str, LLMResponseFormatPropertySchemaModel] = {}
    required: List[str] = []
    additionalProperties: bool = False


class LLmresponseFormatJsonSchemaModel(BaseModel):
    name: str = "schema"
    strict: bool = True
    jsonSchema: LLMResponseFormatJsonSchemaSchemaModel


class LLMResponseFormatModel(BaseModel):
    type: str = "json_schema"
    jsonSchema: LLmresponseFormatJsonSchemaModel


class LLMRequestModel(BaseModel):
    model: str = "llama-3.3-70b"
    messages: List[LLmMessageModel]
    maxCompletionTokens: Optional[int] = 20000
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    apiKey: str
    responseFormat: Optional[LLMResponseFormatModel] = None


class LLMDataChoiceMessageModel(BaseModel):
    role: LLmMessageRoleEnum = LLmMessageRoleEnum.ASSISTANT
    content: str


class LLMDataChoiceModel(BaseModel):
    index: int = 0
    message: LLMDataChoiceMessageModel


class LLMDataUsageModel(BaseModel):
    promptTokens: int | None = None
    completionTokens: int | None = None
    totalTokens: int | None = None


class LLMDataModel(BaseModel):
    id: str
    choices: List[LLMDataChoiceModel] = []
    created: int
    model: str = "llama-3.3-70b"
    totalTime: float = 0.0
    usage: LLMDataUsageModel


class LLMResponseModel(BaseModel):
    status: LLMResponseEnum = LLMResponseEnum.SUCCESS
    LLMData: LLMDataModel | None = None
