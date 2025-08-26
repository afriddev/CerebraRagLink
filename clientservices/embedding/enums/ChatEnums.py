from enum import Enum

class MistralChatMessageRoleEnum(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTENT = "assistant"
    
    
class MistralChatResponseStatusEnum(Enum):
    ERROR  = (500,"ERROR")
    VALIDATION_ERROR = (422, "VALIDATION_ERROR")
    SERVER_ERROR = (500, "SERVER_ERROR")
    SUCCESS = (200, "SUCCESS")



    
    