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
    LLMChatResponseModel,
    HandleQuestionAndAnswersProcessForRagResponseModel,
    TextChunkServiceQuestionAndAnswerWithIdModel,
    ExtractQuestionAndAnswersVectorModel,
)
from rag.services import LLMService, EmbeddingService
from rag.enums import LLMChatMessageRoleEnum
from rag.utils.TextChunkServiceSystemPrompts import (
    ExtarctQuestionAndAnswersFromTextForRagSystemPrompt,
)
from uuid import uuid4
import json

import os
from dotenv import load_dotenv


load_dotenv()


CEREBRAS_API_KEY = cast(Any, os.getenv("CEREBRAS_API_KEY"))


class TextChunkService(TextChunkServiceImpl):

    def ExtractTextFromPdfFile(self, file: str) -> str:
        loader = PyPDFLoader(file)
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

        LLMResponse: LLMChatResponseModel = await llmService.Chat(
            modelParams=LLMChatModel(
                apiKey=CEREBRAS_API_KEY,
                model="qwen-3-235b-a22b-instruct-2507",
                maxCompletionTokens=40000,
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
            data = json.loads(LLMResponse.LLMData.choices[0].message.content)
            data["status"] = LLMResponse.status
            response = ExtarctQuestionAndAnswersFromTextForRagResponseModel.model_validate(
                data
                
            )
            return response
        else:
            return ExtarctQuestionAndAnswersFromTextForRagResponseModel(
                response=None, status=LLMResponse.status
            )

    async def ExtractQuestonAndAnswersForRag(
        self, file: str
    ) -> ExtractQuestionAndAnswersResponseModel:
        text = self.ExtractTextFromPdfFile(file)
        questionAndAnserResponse = await self.ExtractQuestionAndAnswersFromTextForRag(
            text
        )
        if questionAndAnserResponse.response is None:
            return ExtractQuestionAndAnswersResponseModel(
                response=None, status=questionAndAnserResponse.status
            )
        else:
            return ExtractQuestionAndAnswersResponseModel(
                response=questionAndAnserResponse.response,
                status=questionAndAnserResponse.status,
            )

    async def HandleQuestionAndAnswersProcessForRag(
        self, file: str
    ) -> HandleQuestionAndAnswersProcessForRagResponseModel:
        questionAndAnsers = await self.ExtractQuestonAndAnswersForRag(file)
        if questionAndAnsers.response is None:
            return HandleQuestionAndAnswersProcessForRagResponseModel(
                questionAndAnsers=None, status=questionAndAnsers.status, vectors=None
            )
        else:
            embeddingService = EmbeddingService()
            vectors = await embeddingService.ConvertTextToEmbedding(
                [qa.embeddingText for qa in questionAndAnsers.response]
            )
            if vectors.data is None:
                return HandleQuestionAndAnswersProcessForRagResponseModel(
                    status=vectors.status
                )
            else:
                embeddingTexts: list[TextChunkServiceQuestionAndAnswerWithIdModel] = []
                vectorslist: list[ExtractQuestionAndAnswersVectorModel] = []
                for i, q in enumerate(questionAndAnsers.response):
                    embeddingId = uuid4()
                    vectorId = uuid4()
                    embeddingTexts.append(
                        TextChunkServiceQuestionAndAnswerWithIdModel(
                            question=q.question,
                            answer=q.answer,
                            embeddingText=q.embeddingText,
                            id=embeddingId,
                            vectorId=vectorId,
                        )
                    )
                    vectorslist.append(
                        ExtractQuestionAndAnswersVectorModel(
                            embeddingVector=cast(
                                list[float], vectors.data[i].embedding
                            ),
                            id=vectorId,
                            embeddingId=embeddingId,
                        )
                    )

                return HandleQuestionAndAnswersProcessForRagResponseModel(
                    status=vectors.status,
                    questionAndAnsers=embeddingTexts,
                    vectors=vectorslist,
                )
            
