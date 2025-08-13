from abc import ABC, abstractmethod

from models import ConvertTextToEmbeddingResponseErrorModel, ConvertTextToEmbeddingResponseModel


class EmbeddingServiceImpl(ABC):

    @abstractmethod
    async def ConvertTextToEmbedding(
        self, text: list[str]
    ) -> ConvertTextToEmbeddingResponseModel | ConvertTextToEmbeddingResponseErrorModel:
        pass
