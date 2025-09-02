from pydantic import BaseModel
from uuid import UUID


class ChunkMatchedNodeModel_Rag(BaseModel):
    score: float
    chunkId: UUID


class ChunkImagesModel_Rag(BaseModel):
    image: str
    description: str


class CHunkTextsModel_Rag(BaseModel):
    id: UUID
    text: str
    vector: list[float] | None = None
    questions: list[str]
    questionVectors: list[list[float]] | None = []
    images: list[ChunkImagesModel_Rag] | None = None


class ChunkRelationModel_Rag(BaseModel):
    id: UUID
    realtion: str
    relationVector: list[float] | None = None


class ChunkRelationsModel_Rag(BaseModel):
    chunkId: UUID
    chunkRelations: list[ChunkRelationModel_Rag]


class GetRagFromDocResponseModel_Rag(BaseModel):
    chunkTexts: list[CHunkTextsModel_Rag]
    chunkRelations: list[ChunkRelationsModel_Rag]


class ExtarctRelationsAndQuestionFromChunkResponseModel_Rag(BaseModel):
    realtions: list[str]
    questions: list[str]
    chunk: str


class ExatrctImageIndexFromChunkSectionModel_Rag(BaseModel):
    imageindex: int | None
    description: str


class ExatrctImageIndexFromChunkResponseModel_Rag(BaseModel):
    sections: list[ExatrctImageIndexFromChunkSectionModel_Rag]
