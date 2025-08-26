from abc import ABC, abstractmethod
from typing import Tuple
from graphrag.models import HandleChunkRelationExtractResponseModel


class FileChunkGragImpl(ABC):

    @abstractmethod
    def ExatrctChunkFromText(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> Tuple[list[str], list[str]]:
        pass
    
    @abstractmethod
    async def UplaodFileToFirebaseStorage(self, base64Str: str, folder: str) -> str:
        pass

    @abstractmethod
    async def HandleKgChunkRelationExtarctProcess(
        self, file: str
    ) -> HandleChunkRelationExtractResponseModel:
        pass

    @abstractmethod
    async def HandleChunksGraphBuildingProcess(
        self, file: str
    ) -> HandleChunkRelationExtractResponseModel:
        pass

    
