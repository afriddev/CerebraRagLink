from abc import ABC, abstractmethod


class FileChunkGragImpl(ABC):

    @abstractmethod
    def ExatrctChunkFromText(self, file: str, chunkLength: int) -> list[str]:
        pass
    