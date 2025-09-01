from abc import ABC, abstractmethod
from typing import List, Tuple


class ExtractTextFromDocServiceImpl_Rag(ABC):

    @abstractmethod
    def ExtractTextAndImagesFromXlsx_Rag(self, docPath: str) -> Tuple[str, List[str]]:
        pass

    @abstractmethod
    def ExtractTextAndImagesFromCsv_Rag(self, docPath: str) -> Tuple[str, List[str]]:
        pass

    @abstractmethod
    def ExtractTextAndImagesFromDoc_Rag(self, docPath: str) -> Tuple[str, List[str]]:
        pass

    @abstractmethod
    def ExtractTextFromDoc_Rag(self, docPath: str) -> Tuple[str, List[str]]:
        pass
