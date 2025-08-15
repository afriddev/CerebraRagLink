from enum import Enum


class LLMChatMessageRoleEnum(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"




class LLMChatResponseStatusEnum(Enum):
    SUCCESS = (200, "SUCCESS")
    BAD_REQUEST = (400, "BAD_REQUEST")
    UNAUTHROZIED = (401, "UNAUTHROZIED")
    PERMISSION_DENIED = (403, "PERMISSION_DENIED")
    NOT_FOUND = (404, "NOT_FOUND")
    REQUEST_TIMEOUT = (408, "REQUEST_TIMEOUT")
    CONFLICT = (409, "CONFLICT")
    ENTITY_ERROR = (422, "ENTITY_ERROR")
    RATE_LIMIT = (429, "RATE_LIMIT")
    SERVER_ERROR = (500, "SERVER_ERROR")
