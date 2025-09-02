from abc import ABC, abstractmethod
from ragservices.models import (ExtractClaimsAndQuestionsFromChunkResponseModel,BuildRagFromDocResponseModel)

from aiservices import EmbeddingResponseModel, ChatServiceMessageModel


class BuildRagFromDocImpl(ABC):
    @abstractmethod
    async def ExtractClaimsAndQuesFromChunk(
        self,
        messages: list[ChatServiceMessageModel],
        retryLoopIndex: int,
    ) -> ExtractClaimsAndQuestionsFromChunkResponseModel:
        pass

    @abstractmethod
    async def ConvertTextsToVectors(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        pass


    @abstractmethod
    async def HandleEmbeddingsConversion(
        self, file: str
    ) -> BuildRagFromDocResponseModel:
        pass

    @abstractmethod
    async def BuildRagFromDoc(
        self, file: str
    ) -> BuildRagFromDocResponseModel:
        pass
