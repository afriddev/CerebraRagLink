from typing import Any

from rag.qa.implementations import QaAiAnswersImpl
from rag.qa.models import QaAiAnswersRequestModel, QaAiAnswersResponseModel
from clientservices import (
    ChatService,
    ChatServiceMessageModel,
    ChatServiceMessageRoleEnum,
    ChatServiceRequestModel,
)
from clientservices import GetCerebrasApiKey
from rag.qa.utils.qaSystemPropts import QaAiAnswerPromptFromRagText


ChatServices = ChatService()


class QaAiAnswersService(QaAiAnswersImpl):

    async def QaResponse(
        self, request: QaAiAnswersRequestModel
    ) ->  QaAiAnswersResponseModel:

        llmMessages: list[ChatServiceMessageModel] = []
        llmMessages.append(
            ChatServiceMessageModel(
                role=ChatServiceMessageRoleEnum.SYSTEM,
                content=QaAiAnswerPromptFromRagText,
            )
        )

        llmMessages.append(
            ChatServiceMessageModel(
                role=ChatServiceMessageRoleEnum.SYSTEM,
                content=f"Here is the context:\n{request.ragResponseText}",
            )
        )
        

        llmMessages.append(
            ChatServiceMessageModel(role=ChatServiceMessageRoleEnum.USER, content=request.query)
        )

        response:Any = await ChatServices.Chat(
            modelParams=ChatServiceRequestModel(
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
