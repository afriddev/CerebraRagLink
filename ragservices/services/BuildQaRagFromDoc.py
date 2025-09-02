from typing import Any, cast
from ragservices.implementations import BuildQaRagFromDocImpl
from ragservices.models import ExtarctQaResponseModel, BuildQaRagFromDocResponseModel
from aiservices import EmbeddingResponseModel, EmbeddingService, EmbeddingResponseEnum
import re
from ragservices.services.ExtractText import ExtractText

EmbeddingService_Rag = EmbeddingService()
ExtractTextFromDoc = ExtractText()


class BuildQaRagFromDoc(BuildQaRagFromDocImpl):
    def __init__(self):
        self.retryLoopLimit = 3
        self.batchLength = 50

    def ExtarctQaFromText(self, text: str) -> ExtarctQaResponseModel:
        questions = re.findall(r"<<C1-START>>(.*?)<<C1-END>>", text, re.DOTALL)
        answers = re.findall(r"<<C2-START>>(.*?)<<C2-END>>", text, re.DOTALL)
        additionalAnswers = re.findall(r"<<C3-START>>(.*?)<<C3-END>>", text, re.DOTALL)

        combinedAnswer: list[str] = []
        for ans, addAns in zip(answers, additionalAnswers):
            if addAns != "None":
                combinedAnswer.append(f"{ans} Alternative solution is {addAns}")
            else:
                combinedAnswer.append(ans)
        return ExtarctQaResponseModel(questions=questions, answers=answers)

    async def ConvertTextsToVectors(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        if retryLoopIndex > self.retryLoopLimit:
            return EmbeddingResponseModel(status=EmbeddingResponseEnum.ERROR)
        embeddingResponse = await EmbeddingService_Rag.ConvertTextToEmbedding(
            text=texts
        )
        if embeddingResponse.data is None:
            await self.ConvertTextsToVectors(
                texts=texts, retryLoopIndex=retryLoopIndex + 1
            )
        return embeddingResponse

    async def BuildQaRagFromDoc(self, docPath: str) -> BuildQaRagFromDocResponseModel:
        text, _ = ExtractTextFromDoc.ExtractTextFromDoc(docPath=docPath)
        qa = self.ExtarctQaFromText(text=text)
        questionVectors: list[list[float]] = []

        for index in range(0, len(qa.questions), self.batchLength):
            queVecRes = await self.ConvertTextsToVectors(
                retryLoopIndex=0,
                texts=qa.questions[index : index + self.batchLength],
            )
            if queVecRes.data is not None:
                questionVectors.extend(
                    [cast(Any, item.embedding) for item in queVecRes.data]
                )

        return BuildQaRagFromDocResponseModel(
            questions=qa.questions,
            answers=qa.answers,
            questionEmbeddings=questionVectors,
        )
