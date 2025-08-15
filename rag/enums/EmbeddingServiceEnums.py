from enum import Enum

class ConvertTextToEmbeddingResponseErrorEnums(Enum):
    VALIDATION_ERROR = (422, "VALIDATION_ERROR")
    SERVER_ERROR = (500, "SERVER_ERROR")
    SUCCESS = (500, "SUCCESS")
