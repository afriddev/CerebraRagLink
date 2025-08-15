from abc import ABC, abstractmethod

from rag.models import (
    ExtarctQuestionAndAnswersFromTextForRagResponseModel,
    ExtractQuestionAndAnswersResponseModel,
    HandleQuestionAndAnswersProcessForRagResponseModel,
)


class TextChunkServiceImpl(ABC):

    @abstractmethod
    def ExtractTextFromPdfFile(self, file: str) -> str:
        pass

    @abstractmethod
    async def ExtractQuestionAndAnswersFromTextForRag(
        self, text: str
    ) -> ExtarctQuestionAndAnswersFromTextForRagResponseModel:
        pass

    @abstractmethod
    async def ExtractQuestonAndAnswersForRag(
        self, file: str
    ) -> ExtractQuestionAndAnswersResponseModel:
        pass

    @abstractmethod
    async def HandleQuestionAndAnswersProcessForRag(
        self,file:str
    ) -> HandleQuestionAndAnswersProcessForRagResponseModel:
        pass
