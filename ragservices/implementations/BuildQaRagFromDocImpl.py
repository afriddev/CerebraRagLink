from abc import ABC, abstractmethod
from ragservices.models import ExtarctQaResponseModel, BuildQaRagFromDocResponseModel
from aiservices import EmbeddingResponseModel


class BuildQaRagFromDocImpl(ABC):

    @abstractmethod
    def ExtarctQaFromText(self, text: str) -> ExtarctQaResponseModel:
        pass

    @abstractmethod
    async def ConvertTextsToVectors(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        pass

    @abstractmethod
    async def BuildQaRagFromDoc(self, docPath: str) -> BuildQaRagFromDocResponseModel:
        pass
