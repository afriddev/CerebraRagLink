from typing import Any, cast
from rag.implementations import TextChunkServiceImpl
from langchain_community.document_loaders import PyPDFLoader
from rag.models import (
    LLMChatMessageModel,
    LLMChatResponseFormatModel,
    LLMChatResponseFormatJsonSchemaModel,
    LLMChatResponseFormatJsonSchemaSchemaModel,
    LLMChatResponsePropertySchemaModel,
    LLMChatModel,
    ExtarctQuestionAndAnswersFromTextForRagResponseModel,
    ExtractQuestionAndAnswersResponseModel,
    LLMChatResponseModel

)
from rag.services import LLMService
from rag.enums import LLMChatMessageRoleEnum
from rag.utils.TextChunkServiceSystemPrompts import (
    ExtarctQuestionAndAnswersFromTextForRagSystemPrompt,
)


import os
from dotenv import load_dotenv




load_dotenv()


CEREBRAS_API_KEY = cast(Any, os.getenv("CEREBRAS_API_KEY"))


class TextChunkService(TextChunkServiceImpl):

    def ExtractTextFromPdfFile(self, filePath: str) -> str:
        loader = PyPDFLoader(filePath)
        documents = loader.load()
        fullText = "\n".join(doc.page_content for doc in documents)
        return fullText

    async def ExtractQuestionAndAnswersFromTextForRag(
        self, text: str
    ) -> ExtarctQuestionAndAnswersFromTextForRagResponseModel:
        systemPrompt = ExtarctQuestionAndAnswersFromTextForRagSystemPrompt

        llmService = LLMService()
        messages = [
            LLMChatMessageModel(
                role=LLMChatMessageRoleEnum.SYSTEM, content=systemPrompt
            ),
            LLMChatMessageModel(
                role=LLMChatMessageRoleEnum.USER, content=text
            ),  # your PDF-extracted text here
        ]

        LLMResponse:LLMChatResponseModel = await llmService.Chat(
            modelParams=LLMChatModel(
                apiKey=CEREBRAS_API_KEY,
                model="qwen-3-32b",
                maxCompletionTokens=30000,
                messages=messages,
                responseFormat=LLMChatResponseFormatModel(
                    type="json_schema",
                    jsonSchema=LLMChatResponseFormatJsonSchemaModel(
                        name="schema",
                        strict=True,
                        jsonSchema=LLMChatResponseFormatJsonSchemaSchemaModel(
                            type="object",
                            properties={
                                "response": LLMChatResponsePropertySchemaModel(
                                    type="array",
                                    items={
                                        "type": "object",
                                        "properties": {
                                            "question": LLMChatResponsePropertySchemaModel(
                                                type="string"
                                            ),
                                            "answer": LLMChatResponsePropertySchemaModel(
                                                type="string"
                                            ),
                                            "embeddingText": LLMChatResponsePropertySchemaModel(
                                                type="string"
                                            ),
                                        },
                                        "required": [
                                            "question",
                                            "answer",
                                            "embeddingText",
                                        ],
                                        "additionalProperties": False,
                                    },
                                )
                            },
                            required=["response"],
                            additionalProperties=False,
                        ),
                    ),
                ),
            )
        )
        if LLMResponse.LLMData is not None:
            response = ExtarctQuestionAndAnswersFromTextForRagResponseModel.model_validate_json(
                LLMResponse.LLMData.choices[0].message.content
            )
            response.status = LLMResponse.status
            return response
        else:
            return ExtarctQuestionAndAnswersFromTextForRagResponseModel(
                response=None, status=LLMResponse.status
            )

    async def ExtractQuestonAndAnswersForRag(
        self, filePath: str
    ) -> ExtractQuestionAndAnswersResponseModel:
        text = self.ExtractTextFromPdfFile(filePath)
        questionAndAnserResponse = await self.ExtractQuestionAndAnswersFromTextForRag(text)
        if(questionAndAnserResponse.response is None):
            return ExtractQuestionAndAnswersResponseModel(
                response=None, status=questionAndAnserResponse.status
            )
        else:
            return ExtractQuestionAndAnswersResponseModel(
                response=questionAndAnserResponse.response, status=questionAndAnserResponse.status
            )
        


    async def HandleQuestionAndAnswersProcessForRag(self):
