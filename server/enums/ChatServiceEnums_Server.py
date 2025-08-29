from enum import Enum




class ChatServicePreProcessEnums_Server(Enum):
    CONTACT_INFORMATION = "CONTACT_INFO_ERROR"
    ABUSE_LANGUAGE  = "ABUSE_LANG_ERROR"
    OK  = "OK"
    ERROR  = "ERROR"
    LLM = "LLM"
    HMIS = "HMIS"
    
class ChatServicePreProcessRouteEnums_Server(Enum):
    LLM = "LLM"
    HMIS = "HMIs"