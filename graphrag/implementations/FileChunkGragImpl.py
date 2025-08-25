from abc import ABC, abstractmethod
from graphrag.models import HandleChunkRelationExtractResponseModel


class FileChunkGragImpl(ABC):

    @abstractmethod
    def ExatrctChunkFromText(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> list[str]:
        pass

    @abstractmethod
    async def handleKgChunkRelationExtarctProcess(
        self, file: str
    ) -> HandleChunkRelationExtractResponseModel:
        pass

    @abstractmethod
    async def HandleGraphBuildingProcess(self,file:str):
        pass
