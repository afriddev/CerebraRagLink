from abc import ABC, abstractmethod

from rag.models import ConvertTextToEmbeddingResponseErrorModel


class EmbeddingServiceImpl(ABC):

    @abstractmethod
    async def ConvertTextToEmbedding(
        self, text: list[str]
    ) ->  ConvertTextToEmbeddingResponseErrorModel:
        pass
