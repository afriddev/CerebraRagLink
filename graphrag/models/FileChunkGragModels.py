from pydantic import BaseModel




class LLMGragEntityResponseModel(BaseModel):
    entities:list[list[str]]
    relations:list[list[str]]
    context:list[list[str]]