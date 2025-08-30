from typing import Any

from fastapi.responses import StreamingResponse

from server.serviceimplementations import ChatServiceImpl_Server
from aiservices import (
    ChatServiceMessageModel,
    ChatServiceMessageRoleEnum,
    GetCerebrasApiKey,
    ChatServiceRequestModel,
    ChatServiceCerebrasFormatModel,
    ChatServiceCerebrasFormatJsonSchemaModel,
    ChatServiceCerebrasFormatJsonSchemaJsonSchemaModel,
    ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel,
    RerankingRequestModel,
    RerankingResponseModel,
)
from server.models import (
    ChatServiceRequestModel_Server,
    ChatServicePreProcessUserQueryResponseModel_Server,
)

from server.enums import (
    ChatServicePreProcessEnums_Server,
    ChatServicePreProcessRouteEnums_Server,
)
from server.services.GraphRagSearchService_Server import GraphRagSearchService_Server
from server.utils.ChatServiceSystemPrompt_Server import (
    ChatServiceAbusiveUserQuerySystemPrompt_Server,
    ChatServiceConfidentialUserQuerySystemPrompt_Server,
    ChatServicePreProcessUserQuerySystemPropt_Server,
    ChatServiceUserQueryLLMSystemPropt_Server,
)
import json


RetryLoopIndexLimit = 3
graphRagSearchService = GraphRagSearchService_Server()


def getChatLLM():
    from main import ChatLLmService

    return ChatLLmService


def getRankingService():
    from main import RerankingService

    return RerankingService


def getDb():
    from main import psqlDb

    return psqlDb


class ChatService_Server(ChatServiceImpl_Server):

    async def HandlePreProcessUserQuery_Server(
        self, query: str, messages: list[ChatServiceMessageModel], loopIndex: int
    ) -> ChatServicePreProcessUserQueryResponseModel_Server:

        if loopIndex > RetryLoopIndexLimit:
            return ChatServicePreProcessUserQueryResponseModel_Server(
                status=ChatServicePreProcessEnums_Server.ERROR
            )

        response = ChatServicePreProcessUserQueryResponseModel_Server(
            status=ChatServicePreProcessEnums_Server.OK
        )

        LLMResponse: Any = await getChatLLM().Chat(
            modelParams=ChatServiceRequestModel(
                apiKey=GetCerebrasApiKey(),
                model="llama-4-maverick-17b-128e-instruct",
                maxCompletionTokens=500,
                messages=messages,
                temperature=0.0,
                topP=1.0,
                responseFormat=ChatServiceCerebrasFormatModel(
                    type="json_schema",
                    jsonSchema=ChatServiceCerebrasFormatJsonSchemaModel(
                        name="schema",
                        strict=True,
                        jsonSchema=ChatServiceCerebrasFormatJsonSchemaJsonSchemaModel(
                            type="object",
                            properties={
                                "response": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                    type="object",
                                    properties={
                                        "error": {
                                            "type": "string",
                                            "enum": [
                                                "OK",
                                                "ABUSE_LANG_ERROR",
                                                "CONTACT_INFO_ERROR",
                                            ],
                                        },
                                        "route": {
                                            "type": "string",
                                            "enum": ["HMIS", "LLM"],
                                        },
                                    },
                                    required=["error", "route"],
                                    additionalProperties=False,
                                )
                            },
                            required=["response"],
                            additionalProperties=False,
                        ),
                    ),
                ),
            )
        )

        try:
            LLMResponse = json.loads(
                LLMResponse.LLMData.choices[0].message.content
            ).get("response")

            if LLMResponse.get("error") == "OK":
                response.status = ChatServicePreProcessEnums_Server.OK
                if LLMResponse.get("route") == "HMIS":
                    response.route = ChatServicePreProcessRouteEnums_Server.HMIS
                else:
                    response.route = ChatServicePreProcessRouteEnums_Server.LLM

            elif LLMResponse.get("error") == "ABUSE_LANG_ERROR":
                response.status = ChatServicePreProcessEnums_Server.ABUSE_LANGUAGE
                response.route = ChatServicePreProcessRouteEnums_Server.LLM

            elif LLMResponse.get("error") == "CONTACT_INFO_ERROR":
                response.status = ChatServicePreProcessEnums_Server.CONTACT_INFORMATION
                response.route = ChatServicePreProcessRouteEnums_Server.LLM

        except Exception as _:
            messages.append(
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content="Please generate a valid json",
                )
            )
            await self.HandlePreProcessUserQuery_Server(
                query=query, messages=messages, loopIndex=loopIndex + 1
            )
        return response

    async def LLMChat_Server(
        self, messages: list[ChatServiceMessageModel]
    ) -> StreamingResponse | None:
        try:
            LLMResponse: Any = await getChatLLM().Chat(
                modelParams=ChatServiceRequestModel(
                    apiKey=GetCerebrasApiKey(),
                    model="gpt-oss-120b",
                    maxCompletionTokens=10000,
                    messages=messages,
                    stream=True,
                    temperature=0.8,
                    topP=0.9,
                )
            )
            return LLMResponse

        except Exception as e:
            return None

    async def ChatService_Server(
        self, request: ChatServiceRequestModel_Server
    ) -> StreamingResponse:
        preProcessMessages: list[ChatServiceMessageModel] = [
            ChatServiceMessageModel(
                role=ChatServiceMessageRoleEnum.SYSTEM,
                content=ChatServicePreProcessUserQuerySystemPropt_Server,
            ),
            ChatServiceMessageModel(
                role=ChatServiceMessageRoleEnum.USER,
                content=request.query,
            ),
        ]

        preProcessResponse: ChatServicePreProcessUserQueryResponseModel_Server = (
            await self.HandlePreProcessUserQuery_Server(
                messages=preProcessMessages, loopIndex=0, query=request.query
            )
        )

        if preProcessResponse.route != ChatServicePreProcessRouteEnums_Server.HMIS:
            messages: list[ChatServiceMessageModel] = []
            if (
                preProcessResponse.status
                == ChatServicePreProcessEnums_Server.ABUSE_LANGUAGE
            ):
                messages.append(
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.SYSTEM,
                        content=ChatServiceAbusiveUserQuerySystemPrompt_Server,
                    )
                )

            if (
                preProcessResponse.status
                == ChatServicePreProcessEnums_Server.CONTACT_INFORMATION
            ):
                messages.append(
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.SYSTEM,
                        content=ChatServiceConfidentialUserQuerySystemPrompt_Server,
                    )
                )

            if preProcessResponse.status == ChatServicePreProcessEnums_Server.OK:
                messages.append(
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.SYSTEM,
                        content=ChatServiceUserQueryLLMSystemPropt_Server,
                    )
                )
            messages.append(
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content=request.query,
                )
            )

            response = await self.LLMChat_Server(messages=messages)
            if response is not None:
                return response
            return StreamingResponse(
                iter([b"Sorry, Something went wrong !. Please Try again?"])
            )
        else:
            graphRagServiceResponse = await graphRagSearchService.SearchOnDb_Server(
                query=request.query, db=getDb()
            )

            topRerankingResponse: (
                RerankingResponseModel
            ) = await getRankingService().FindRankingScore(
                RerankingRequestModel(
                    model="jina-reranker-m0",
                    query=request.query,
                    docs=graphRagServiceResponse,
                    topN=10,
                )
            )

            topDocs: list[str] = []

            for i, doc in enumerate(topRerankingResponse.response):
                index = doc.index
                topDocs.append(graphRagServiceResponse[index])

            ctx = "\n\n".join(f"[{k+1}] {t}" for k, t in enumerate(topDocs))

            print(ctx)
            system_msg = f"""
# Retrieved Context
{ctx}

# Instructions
- Use ONLY the Retrieved Context above to answer the user's query.
- If an image description in the context is relevant to the query, include its image URL in your answer.
- If the user indirectly asks for something that the image illustrates, also provide the matching image URL.
- If no relevant answer or image exists in the context, respond with: "I don't have enough information."
- Keep the answer clear and concise.
"""

            messages: list[ChatServiceMessageModel] = [
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.SYSTEM,
                    content=system_msg,
                ),
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content=request.query,
                ),
            ]

            response = await self.LLMChat_Server(messages=messages)
            return response
