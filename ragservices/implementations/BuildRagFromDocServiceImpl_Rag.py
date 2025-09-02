from abc import ABC, abstractmethod
from ragservices.models import (
    GetRagFromDocResponseModel_Rag,
    ExtarctRelationsAndQuestionFromChunkResponseModel_Rag,
    ExatrctImageIndexFromChunkResponseModel_Rag,
)

from aiservices import EmbeddingResponseModel, ChatServiceMessageModel


class BuildRagFromDocServiceImpl_Rag(ABC):



    @abstractmethod
    async def ExtarctRelationsAndQuestionFromChunk_Rag(
        self,
        messages: list[ChatServiceMessageModel],
        retryLoopIndex: int,
    ) -> ExtarctRelationsAndQuestionFromChunkResponseModel_Rag:
        pass

    @abstractmethod
    async def ConvertTextsToVectorsFromChunk_Rag(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        pass

    @abstractmethod
    async def ExatrctImageIndexFromChunk_Rag(
        self,
        messages: list[ChatServiceMessageModel],
        chunkText: str,
        retryLoopIndex: int,
    ) -> ExatrctImageIndexFromChunkResponseModel_Rag:
        pass

    @abstractmethod
    async def ExtractChunksAndRelationsFromDoc_Rag(
        self, file: str
    ) -> GetRagFromDocResponseModel_Rag:
        pass

    @abstractmethod
    async def BuildRagFromDoc_Rag(
        self, file: str
    ) -> GetRagFromDocResponseModel_Rag:
        pass
