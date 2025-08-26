from pydantic import BaseModel
from uuid import UUID


class LLMGragEntityResponseModel(BaseModel):
    relations: list[list[str]]
    relationshipsEntities: list[list[list[str]]]
    chunk: list[str]


class ChunkNodeModel(BaseModel):
    score: float
    chunkId: UUID


class ChunkImagesData(BaseModel):
    sectionNumber: float
    title: str
    image: str
    description: str


class ChunkTextsModel(BaseModel):
    id: UUID
    text: str
    vector: list[float] | None = None
    entities: list[str]
    questions: list[str]
    questionVectors: list[list[float]] | None = []
    matchedNodes: list[ChunkNodeModel] | None = None
    images: list[ChunkImagesData] | None = None


class ChunkRelationModel(BaseModel):
    id: UUID
    realtion: str
    realtionEntites: list[str]
    relationVector: list[float] | None = None


class ChunkRelationsModel(BaseModel):
    chunkId: UUID
    chunkRelations: list[ChunkRelationModel]


class HandleChunkRelationExtractResponseModel(BaseModel):
    chunkTexts: list[ChunkTextsModel]
    chunkRelations: list[ChunkRelationsModel]
