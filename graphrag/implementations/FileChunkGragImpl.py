from abc import ABC, abstractmethod


class FileChunkGragImpl(ABC):

    @abstractmethod
    def ExatrctChunkFromText(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> list[str]:
        pass

    async def handleEntitiesProcess(self, file: str):
        pass
