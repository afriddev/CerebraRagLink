from pydantic import BaseModel
from uuid import UUID


class ChunkTextsModel(BaseModel):
    id: UUID
    text: str
    embedding: list[float] | None = None


class ChunkQuestionsModel(BaseModel):
    chunkId: UUID
    questions: list[str]
    questionEmbeddings: list[list[float]] | None = []


class ChunkClaimsModel(BaseModel):
    chunkId: UUID
    claims: list[str]
    ClaimEmbeddings: list[list[float]] | None = None


class ExtractClaimsAndQuestionsFromChunkResponseModel(BaseModel):
    chunk: str
    questions: list[str]
    claims: list[str]


class BuildRagFromDocResponseModel(BaseModel):
    chunkTexts: list[ChunkTextsModel]
    chunkClaims: list[ChunkClaimsModel]
    chunkQuestion: list[ChunkQuestionsModel]
