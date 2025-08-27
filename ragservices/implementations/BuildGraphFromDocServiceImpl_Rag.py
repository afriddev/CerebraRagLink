from abc import ABC, abstractmethod
from typing import Tuple
from ragservices.models import GetGraphFromDocResponseModel_Rag


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
    async def ExtractChunksAndRelationsFromDoc_Rag(
        self, file: str
    ) -> GetGraphFromDocResponseModel_Rag:
        pass

    @abstractmethod
    async def BuildGraphFromDoc_Rag(self, file: str) -> GetGraphFromDocResponseModel_Rag:
        pass
