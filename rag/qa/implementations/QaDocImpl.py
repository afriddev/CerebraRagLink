from abc import ABC, abstractmethod

from rag.qa.models import (
    ExtarctQaFromTextResponseModel,
    ExtractQaResponseModel,
    HandleQaExtractResponseModel,
)


class QaDocImpl(ABC):

    

    @abstractmethod
    async def ExtractQaFromText(
        self, text: str
    ) -> ExtarctQaFromTextResponseModel:
        pass

    @abstractmethod
    async def ExtractQa(
        self, file: str
    ) -> ExtractQaResponseModel:
        pass

    @abstractmethod
    async def HandleQaExtract(
        self,file:str
    ) -> HandleQaExtractResponseModel:
        pass
