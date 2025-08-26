from abc import ABC, abstractmethod

from aiservices.embedding.models import EmbeddingResponseModel


class EmbeddingServiceImpl(ABC):

    @abstractmethod
    async def ConvertTextToEmbedding(self, text: list[str]) -> EmbeddingResponseModel:
        pass

    @abstractmethod
    def FindSimilarity(self, vec1: list[float], vec2: list[float]) -> float:
        pass
