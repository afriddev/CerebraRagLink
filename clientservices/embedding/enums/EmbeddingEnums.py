from enum import Enum

class EmbeddingResponseEnum(Enum):
    VALIDATION_ERROR = (422, "VALIDATION_ERROR")
    SERVER_ERROR = (500, "SERVER_ERROR")
    SUCCESS = (200, "SUCCESS")
