from typing import Any, cast
from ragservices.implementations import BuildQaRagFromDocImpl_Rag
from ragservices.models import (
    ExtarctQuestionAndAnswersFromDocResponse_Rag,
    HandleQaRagBuildingProcessResponseModel_Rag,
)
from aiservices import EmbeddingResponseModel, EmbeddingService, EmbeddingResponseEnum
import re
from ragservices.services.ExtractTextFromDocService_Rag import ExtractTextFromDocService

EmbeddingService_Rag = EmbeddingService()
ExtractedTextFromDocService_rag = ExtractTextFromDocService()


class BuildQaRagFromDocService_Rag(BuildQaRagFromDocImpl_Rag):
    def __init__(self):
        self.RetryLoopIndexLimit = 3
        self.batchLength = 50

    def ExtarctQuesionAndAnsersFromDocText_Rag(
        self, text: str
    ) -> ExtarctQuestionAndAnswersFromDocResponse_Rag:
        questionList = re.findall(r"<<R1-START>>(.*?)<<R1-END>>", text, re.DOTALL)
        answersList = re.findall(r"<<R2-START>>(.*?)<<R2-END>>", text, re.DOTALL)
        return ExtarctQuestionAndAnswersFromDocResponse_Rag(
            questions=questionList, answers=answersList
        )

    async def ConvertTextsToVectorsFrom_Rag(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        if retryLoopIndex > self.RetryLoopIndexLimit:
            return EmbeddingResponseModel(status=EmbeddingResponseEnum.ERROR)
        embeddingResponse = await EmbeddingService_Rag.ConvertTextToEmbedding(
            text=texts
        )
        if embeddingResponse.data is None:
            await self.ConvertTextsToVectorsFrom_Rag(
                texts=texts, retryLoopIndex=retryLoopIndex + 1
            )
        return embeddingResponse

    async def HandleQaRagBuildingProcess_Rag(
        self, docPath: str
    ) -> HandleQaRagBuildingProcessResponseModel_Rag:
        extractedText, _ = ExtractedTextFromDocService_rag.ExtractTextFromDoc_Rag(
            docPath=docPath
        )
        questionAndAnswers = self.ExtarctQuesionAndAnsersFromDocText_Rag(
            text=extractedText
        )
        print(questionAndAnswers)
        questionVectors: list[list[float]] = []

        for index in range(0, len(questionAndAnswers.questions), self.batchLength):
            batchQuestionsVectorResponse = await self.ConvertTextsToVectorsFrom_Rag(
                retryLoopIndex=0,
                texts=questionAndAnswers.questions[index : index + self.batchLength],
            )
            if batchQuestionsVectorResponse.data is not None:
                questionVectors.extend(
                    [
                        cast(Any, item.embedding)
                        for item in batchQuestionsVectorResponse.data
                    ]
                )

        return HandleQaRagBuildingProcessResponseModel_Rag(
            questions=questionAndAnswers.questions,
            answers=questionAndAnswers.answers,
            questionVectors=questionVectors,
        )
