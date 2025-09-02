from typing import Any, cast

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
)
from server.models import (
    ChatServiceRequestModel_Server,
    ChatServicePreProcessUserQueryResponseModel_Server,
)
from server.enums import (
    ChatServicePreProcessEnums_Server,
    ChatServicePreProcessRouteEnums_Server,
)
from server.services.RagSearchService_Server import RagSearchService_Server
from server.utils.ChatServiceSystemPrompt_Server import (
    ChatServiceAbusiveUserQuerySystemPrompt_Server,
    ChatServiceConfidentialUserQuerySystemPrompt_Server,
    ChatServicePreProcessUserQuerySystemPropt_Server,
    ChatServiceUserQueryLLMSystemPropt_Server,
)
from server.models import SearchOnDbResponseModel
import json


RetryLoopIndexLimit = 3
RagSearchService = RagSearchService_Server()


def getChatLLM():
    from main import ChatLLmService

    return ChatLLmService


def getRankingService():
    from main import RerankingService

    return RerankingService


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
                model="llama-4-scout-17b-16e-instruct",
                maxCompletionTokens=1000,
                messages=messages,
                temperature=0.2,
                topP=0.9,
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
                                        "cleanquery": {"type": "string"},
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
                    response.cleanquery = LLMResponse.get("cleanquery")
                else:
                    response.route = ChatServicePreProcessRouteEnums_Server.LLM
                    response.cleanquery = LLMResponse.get("cleanquery")

            elif LLMResponse.get("error") == "ABUSE_LANG_ERROR":
                response.status = ChatServicePreProcessEnums_Server.ABUSE_LANGUAGE
                response.route = ChatServicePreProcessRouteEnums_Server.LLM
                response.cleanquery = LLMResponse.get("cleanquery")

            elif LLMResponse.get("error") == "CONTACT_INFO_ERROR":
                response.status = ChatServicePreProcessEnums_Server.CONTACT_INFORMATION
                response.route = ChatServicePreProcessRouteEnums_Server.LLM
                response.cleanquery = LLMResponse.get("cleanquery")

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
                    maxCompletionTokens=5000,
                    messages=messages,
                    stream=True,
                    temperature=0.8,
                    topP=0.9,
                )
            )
            return LLMResponse

        except Exception as _:
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
        print(preProcessResponse.cleanquery)

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
                    content=cast(Any, preProcessResponse.cleanquery),
                )
            )

            response = await self.LLMChat_Server(messages=messages)
            if response is not None:
                return response
            return StreamingResponse(
                iter([b"Sorry, Something went wrong !. Please Try again?"])
            )
        else:
            ragServiceResponse: SearchOnDbResponseModel = (
                await RagSearchService.SearchOnDb_Server(
                    query=cast(Any, preProcessResponse.cleanquery)
                )
            )
            docs = [doc.matchedText for doc in ragServiceResponse.docs]

            topRerankingDocsResponse = await getRankingService().FindRankingScore(
                RerankingRequestModel(
                    model="jina-reranker-m0",
                    query=cast(Any, preProcessResponse.cleanquery),
                    docs=docs,
                    topN=10,
                )
            )

            topDocs: list[str] = []

            if topRerankingDocsResponse.response is not None:
                reranked = sorted(
                    topRerankingDocsResponse.response,
                    key=lambda x: x.score,
                    reverse=True,
                )

                topK = reranked[:7]

                for item in topK:
                    index = item.index
                    doc = ""
                    doc += f"Matched Text: {ragServiceResponse.docs[index].matchedText}\nContext: {ragServiceResponse.docs[index].contextText}"

                    for img in ragServiceResponse.docs[index].images:
                        doc += f"\nImage:\n- Description: {img.description}\n- URL: {img.url}"

                    topDocs.append(doc)

            systemInst = f"""
                # Retrieved docs
                {json.dumps(topDocs, indent=2)}

                # Instructions
                - Write answers concisely and proportional to the query:
                - Short/fact-based (2–3 marks): answer in 2–3 sentences.
                - Explanation (10 marks): answer in clear, structured detail (use headings, bullet points, or numbered lists).
                - Formatting rules:
                - Use clean **Markdown** only (no tables unless explicitly requested).
                - Always use headings (###) for clarity in longer answers.
                - Keep answers professional, without unnecessary filler text.
                - Images:
                - By default, include only **one most relevant image**.
                - If the user explicitly asks for multiple images, include all relevant ones.
                - Show each image as:
                    **Description**  
                    ![alt text](URL)
                - If the image is too large or detailed, use:
                    <img src="URL" width="600"/>
                - Never embed images inside tables.
                - If no relevant info exists in the retrieved docs, reply with exactly:
                "We don’t have information about this. Please contact the helpdesk for further assistance."
                    """

            messages: list[ChatServiceMessageModel] = [
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.SYSTEM,
                    content=systemInst,
                ),
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content=cast(Any, preProcessResponse.cleanquery),
                ),
            ]

            response = await self.LLMChat_Server(messages=messages)
            if response is not None:
                return response
            else:
                return StreamingResponse(
                    iter([b"Sorry, Something went wrong !. Please Try again?"])
                )
