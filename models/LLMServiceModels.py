from typing import List, Optional
from pydantic import BaseModel
from enums import (
    LLMChatMessageRoleEnum,
    LLMChatReasoningEffortEnum,
    LLMChatResponseStatusEnum,
)


class LLMChatMessageModel(BaseModel):
    role: Optional[LLMChatMessageRoleEnum] = LLMChatMessageRoleEnum.USER
    content: str


class LLMChatModel(BaseModel):
    model: str = "llama3.1-8b"
    messages: List[LLMChatMessageModel]
    maxCompletionTokens: Optional[int] = 100
    reasoningEffort: LLMChatReasoningEffortEnum = LLMChatReasoningEffortEnum.MEDIUM
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    apiKey: str


class LLMChatResponseModel(BaseModel):
    status: LLMChatResponseStatusEnum = LLMChatResponseStatusEnum.SUCCESS
