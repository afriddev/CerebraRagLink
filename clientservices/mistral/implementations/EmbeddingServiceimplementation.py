from abc import ABC, abstractmethod

from clientservices.mistral.models import EmbeddingResponseModel


class EmbeddingServiceImpl(ABC):

    @abstractmethod
    async def ConvertTextToEmbedding(
        self, text: list[str]
    ) ->  EmbeddingResponseModel:
        pass
