from typing import Any, cast
from rag.qa.implementations import QaDocImpl
from clientservices import (
    LLMMessageModel,
    LLMResponseFormatModel,
    LLmresponseFormatJsonSchemaModel,
    LLMResponseFormatJsonSchemaSchemaModel,
    LLMResponseFormatPropertySchemaModel,
    LLMRequestModel,
    LLMService,
    EmbeddingService,
    LLmMessageRoleEnum,
)
from rag.qa.models import (
    HandleQaExtractResponseModel,
    ExtractQaEmbeddingVectorModel,
    ExtractQaVectorModel,
    ExtarctQaFromTextResponseModel,
    ExtractQaResponseModel,
)
from clientservices import GetCerebrasApiKey
from uuid import uuid4
import json
from rag.qa.utils.qaSystemPropts import ExtractQaPrompt
from utils import ExtractTextFromDoc

llmService = LLMService()
embeddingService = EmbeddingService()


class QaDocService(QaDocImpl):

    async def ExtractQaFromText(self, text: str) -> ExtarctQaFromTextResponseModel:
        systemPrompt = ExtractQaPrompt

        messages = [
            LLMMessageModel(role=LLmMessageRoleEnum.SYSTEM, content=systemPrompt),
            LLMMessageModel(
                role=LLmMessageRoleEnum.USER, content=text
            ),  # your PDF-extracted text here
        ]

        LLMResponse: Any = await llmService.Chat(
            modelParams=LLMRequestModel(
                apiKey=GetCerebrasApiKey(),
                model="qwen-3-coder-480b",
                maxCompletionTokens=30000,
                messages=messages,
                responseFormat=LLMResponseFormatModel(
                    type="json_schema",
                    jsonSchema=LLmresponseFormatJsonSchemaModel(
                        name="schema",
                        strict=True,
                        jsonSchema=LLMResponseFormatJsonSchemaSchemaModel(
                            type="object",
                            properties={
                                "response": LLMResponseFormatPropertySchemaModel(
                                    type="array",
                                    items={
                                        "type": "object",
                                        "properties": {
                                            "question": LLMResponseFormatPropertySchemaModel(
                                                type="string"
                                            ),
                                            "answer": LLMResponseFormatPropertySchemaModel(
                                                type="string"
                                            ),
                                            "embeddingText": LLMResponseFormatPropertySchemaModel(
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
        print(LLMResponse.LLMData.choices[0].message.content)
        if LLMResponse.LLMData is not None:
            data = json.loads(LLMResponse.LLMData.choices[0].message.content)
            data["status"] = LLMResponse.status
            response = ExtarctQaFromTextResponseModel.model_validate(data)
            return response
        else:
            return ExtarctQaFromTextResponseModel(
                response=None, status=LLMResponse.status
            )

    async def ExtractQa(self, file: str) -> ExtractQaResponseModel:
        text = ExtractTextFromDoc(file)
        questionAndAnserResponse = await self.ExtractQaFromText(text)
        if questionAndAnserResponse.response is None:
            return ExtractQaResponseModel(
                response=None, status=questionAndAnserResponse.status
            )
        else:
            return ExtractQaResponseModel(
                response=questionAndAnserResponse.response,
                status=questionAndAnserResponse.status,
            )

    async def HandleQaExtract(self, file: str) -> HandleQaExtractResponseModel:
        questionAndAnsers = await self.ExtractQa(file)
        if questionAndAnsers.response is None:
            return HandleQaExtractResponseModel(
                questionAndAnsers=None, status=questionAndAnsers.status, vectors=None
            )
        else:
            vectors = await embeddingService.ConvertTextToEmbedding(
                [qa.embeddingText for qa in questionAndAnsers.response]
            )
            if vectors.data is None:
                return HandleQaExtractResponseModel(status=vectors.status)
            else:
                embeddingTexts: list[ExtractQaEmbeddingVectorModel] = []
                vectorslist: list[ExtractQaVectorModel] = []
                for i, q in enumerate(questionAndAnsers.response):
                    embeddingId = uuid4()
                    vectorId = uuid4()
                    embeddingTexts.append(
                        ExtractQaEmbeddingVectorModel(
                            question=q.question,
                            answer=q.answer,
                            embeddingText=q.embeddingText,
                            id=embeddingId,
                            vectorId=vectorId,
                        )
                    )
                    vectorslist.append(
                        ExtractQaVectorModel(
                            embeddingVector=cast(
                                list[float], vectors.data[i].embedding
                            ),
                            id=vectorId,
                            embeddingId=embeddingId,
                        )
                    )

                return HandleQaExtractResponseModel(
                    status=vectors.status,
                    questionAndAnsers=embeddingTexts,
                    vectors=vectorslist,
                )
