from abc import ABC, abstractmethod
from typing import List, Tuple


class ExtractTextImpl(ABC):

    @abstractmethod
    def ExtractTextAndImagesFromXlsx(self, docPath: str) -> Tuple[str, List[str]]:
        pass

    @abstractmethod
    def ExtractTextAndImagesFromCsv(self, docPath: str) -> Tuple[str, List[str]]:
        pass

    @abstractmethod
    def ExtractTextAndImagesFromDoc(self, docPath: str) -> Tuple[str, List[str]]:
        pass

    @abstractmethod
    def ExtractTextFromDoc(self, docPath: str) -> Tuple[str, List[str]]:
        pass
