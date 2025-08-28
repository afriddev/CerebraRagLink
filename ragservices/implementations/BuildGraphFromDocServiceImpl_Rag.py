from abc import ABC, abstractmethod
from typing import Tuple
from ragservices.models import (
    GetGraphFromDocResponseModel_Rag,
    ExtarctRelationsAndQuestionFromChunkResponseModel_Rag,
    ExatrctImageIndexFromChunkResponseModel_Rag,
)

from aiservices import EmbeddingResponseModel, ChatServiceMessageModel


class BuildGraphFromDocServiceImpl_Rag(ABC):

    @abstractmethod
    def ExtractChunksFromDoc_Rag(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> Tuple[list[str], list[str]]:
        pass

    @abstractmethod
    async def UploadImagesFromDocToFirebase_Rag(
        self, base64Str: str, folder: str
    ) -> str:
        pass

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
    ) -> GetGraphFromDocResponseModel_Rag:
        pass

    @abstractmethod
    async def BuildGraphFromDoc_Rag(
        self, file: str
    ) -> GetGraphFromDocResponseModel_Rag:
        pass
