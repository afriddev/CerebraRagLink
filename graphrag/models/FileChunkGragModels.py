from pydantic import BaseModel
from uuid import UUID


class LLMGragEntityResponseModel(BaseModel):
    entities: list[list[str]]
    relations: list[list[str]]
    relationshipsEntities: list[list[list[str]]]
    chunk: list[str]


class ChunkTextsModel(BaseModel):
    id: UUID
    text: str
    vector:list[float] | None  = None


class ChunkRelationModel(BaseModel):
    realtion: str
    realtionEntites: list[str]


class ChunkRelationsModel(BaseModel):
    chunkId: UUID
    chunkRelations: list[ChunkRelationModel]


class ChunkEntitiesModel(BaseModel):
    chunkId: UUID
    chunkEntities: list[str]


class ChunkTextVectors