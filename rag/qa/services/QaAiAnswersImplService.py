from typing import Any

from rag.qa.implementations import QaAiAnswersImpl
from rag.qa.models import QaAiAnswersRequestModel, QaAiAnswersResponseModel
from clientservices import (
    LLMService,
    LLMMessageModel,
    LLmMessageRoleEnum,
    LLMRequestModel,
)
from clientservices import GetCerebrasApiKey
from rag.qa.utils.qaSystomPropts import QaAiAnswerPromptFromRagText


llmServices = LLMService()


class QaAiAnswersService(QaAiAnswersImpl):

    async def QaResponse(
        self, request: QaAiAnswersRequestModel
    ) ->  QaAiAnswersResponseModel:

        llmMessages: list[LLMMessageModel] = []
        llmMessages.append(
            LLMMessageModel(
                role=LLmMessageRoleEnum.SYSTEM,
                content=QaAiAnswerPromptFromRagText,
            )
        )

        llmMessages.append(
            LLMMessageModel(
                role=LLmMessageRoleEnum.SYSTEM,
                content=f"Here is the context:\n{request.ragResponseText}",
            )
        )
        

        llmMessages.append(
            LLMMessageModel(role=LLmMessageRoleEnum.USER, content=request.query)
        )

        response:Any = await llmServices.Chat(
            modelParams=LLMRequestModel(
                apiKey=GetCerebrasApiKey(),
                model="llama-4-scout-17b-16e-instruct",
                stream=False,
                messages=llmMessages,
                responseFormat=None,
                temperature=0.2,
                maxCompletionTokens=1000,
            )
        )
        return QaAiAnswersResponseModel(
            status=response.status,
            response=response.LLMData.choices[0].message.content
            
        )
