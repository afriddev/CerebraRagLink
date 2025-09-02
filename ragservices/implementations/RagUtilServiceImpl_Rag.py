from abc import ABC, abstractmethod
from typing import Tuple


class RagUtilServiceImpl(ABC):

    @abstractmethod
    def ExtractChunksFromText(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> Tuple[list[str], list[str]]:
        pass

