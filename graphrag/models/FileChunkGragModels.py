from pydantic import BaseModel


class LLMGragEntityResponseModel(BaseModel):
    entities: list[list[str]]
    relations: list[list[str]]
    relationshipsEntities: list[list[list[str]]]
    chunks: list[str]

