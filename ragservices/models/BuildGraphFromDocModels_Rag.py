from pydantic import BaseModel
from uuid import UUID


class ChunkMatchedNodeModel_Rag(BaseModel):
    score: float
    chunkId: UUID


class ChunkImagesModel_Rag(BaseModel):
    sectionNumber: float 
    title: str
    image: str
    description: str


class CHunkTextsModel_Rag(BaseModel):
    id: UUID
    text: str
    vector: list[float] | None = None
    entities: list[str]
    questions: list[str]
    questionVectors: list[list[float]] | None = []
    matchedNodes: list[ChunkMatchedNodeModel_Rag] | None = None
    images: list[ChunkImagesModel_Rag] | None = None


class ChunkRelationModel_Rag(BaseModel):
    id: UUID
    realtion: str
    realtionEntites: list[str]
    relationVector: list[float] | None = None


class ChunkRelationsModel_Rag(BaseModel):
    chunkId: UUID
    chunkRelations: list[ChunkRelationModel_Rag]


class GetGraphFromDocResponseModel_Rag(BaseModel):
    chunkTexts: list[CHunkTextsModel_Rag]
    chunkRelations: list[ChunkRelationsModel_Rag]
