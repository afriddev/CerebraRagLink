from pydantic import BaseModel
from uuid import UUID


class LLMGragEntityResponseModel(BaseModel):
    relations: list[list[str]]
    relationshipsEntities: list[list[list[str]]]
    chunk: list[str]


class ChunkTextsModel(BaseModel):
    id: UUID
    text: str
    vector: list[float] | None = None
    entities: list[str]



class ChunkRelationModel(BaseModel):
    id: UUID
    realtion: str
    realtionEntites: list[str]
    relationVector: list[float] | None = None


class ChunkRelationsModel(BaseModel):
    chunkId: UUID
    chunkRelations: list[ChunkRelationModel]


    

class HandleKgExatrctProcessResponseModel(BaseModel):
    chunkTexts: list[ChunkTextsModel]
    chunkRelations: list[ChunkRelationsModel]