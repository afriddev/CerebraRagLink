from abc import ABC, abstractmethod

from rag.models import (
    ExtarctQuestionAndAnswersFromTextForRagResponseModel,
    ExtractQuestionAndAnswersResponseModel,
)


class TextChunkServiceImpl(ABC):

    @abstractmethod
    def ExtractTextFromPdfFile(self, filePath: str) -> str:
        pass

    @abstractmethod
    async def ExtractQuestionAndAnswersFromTextForRag(
        self, text: str
    ) -> ExtarctQuestionAndAnswersFromTextForRagResponseModel:
        pass

    @abstractmethod
    async def ExtractQuestonAndAnswersForRag(
        self, filePath: str
    ) -> ExtractQuestionAndAnswersResponseModel:
        pass
