from typing import Any, cast
from aiservices import (
    ChatServiceCerebrasFormatJsonSchemaJsonSchemaModel,
    ChatService,
    ChatServiceRequestModel,
    GetCerebrasApiKey,
    ChatServiceCerebrasFormatModel,
    ChatServiceCerebrasFormatJsonSchemaModel,
    ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel,
    ChatServiceMessageModel,
    ChatServiceMessageRoleEnum,
    EmbeddingService,
    RerankingService,
    EmbeddingResponseModel,
    EmbeddingResponseEnum,
)
from ragservices.implementations import BuildRagFromDocImpl

import json
from ragservices.models import (
    ChunkClaimsModel,
    ChunkTextsModel,
    ExtractClaimsAndQuestionsFromChunkResponseModel,
    BuildRagFromDocResponseModel,
    ChunkQuestionsModel,
)
from uuid import uuid4
from ragservices.services.RagUtils import RagUtilS
from ragservices.utils.BuildRagFromDocSystemPrompts import (
    ExtractClaimsAndQuestionsFromChunkSystemPrompt,
)


chatService = ChatService()
embeddingService = EmbeddingService()
rerankingService = RerankingService()
RagUtilService = RagUtilS()


class BuildRagFromDoc(BuildRagFromDocImpl):

    def __init__(self):
        self.RetryLoopIndexLimit = 3

    async def ExtractClaimsAndQuesFromChunk(
        self,
        messages: list[ChatServiceMessageModel],
        retryLoopIndex: int,
    ) -> ExtractClaimsAndQuestionsFromChunkResponseModel:
        if retryLoopIndex > self.RetryLoopIndexLimit:
            raise Exception(
                "Exception while extarcting relation and questions from chunk"
            )

        LLMChunkResponse: Any = await chatService.Chat(
            modelParams=ChatServiceRequestModel(
                apiKey=GetCerebrasApiKey(),
                model="qwen-3-235b-a22b-instruct-2507",
                maxCompletionTokens=30000,
                messages=messages,
                temperature=0.0,
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
                                        "claims": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                            type="array",
                                            items={"type": "string"},
                                        ),
                                        "questions": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                            type="array",
                                            items={"type": "string"},
                                        ),
                                        "chunk": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                            type="string"
                                        ),
                                    },
                                    required=[
                                        "claims",
                                        "chunk",
                                        "questions",
                                    ],
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
        LLMResponse: Any = {}
        try:

            LLMResponse = json.loads(
                LLMChunkResponse.LLMData.choices[0].message.content
            ).get("response")

        except Exception as e:
            print("Error occured while extracting realtions from chunk retrying ...")
            print(e)
            messages.append(
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content="Please generate a valid json object",
                )
            )

            await self.ExtractClaimsAndQuesFromChunk(
                messages=messages,
                retryLoopIndex=retryLoopIndex + 1,
            )
        response = ExtractClaimsAndQuestionsFromChunkResponseModel(
            chunk=LLMResponse.get("chunk"),
            questions=LLMResponse.get("questions"),
            claims=LLMResponse.get("claims"),
        )
        return response

    async def ConvertTextsToVectors(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        if retryLoopIndex > self.RetryLoopIndexLimit:
            return EmbeddingResponseModel(status=EmbeddingResponseEnum.ERROR)

        embeddingResponse = await embeddingService.ConvertTextToEmbedding(text=texts)
        if embeddingResponse.data is None:
            await self.ConvertTextsToVectors(
                texts=texts, retryLoopIndex=retryLoopIndex + 1
            )
        return embeddingResponse

    async def HandleEmbeddingsConversion(
        self, file: str
    ) -> BuildRagFromDocResponseModel:
        chunks, _ = RagUtilService.ExtractChunksFromText(file, 600)

        chunkTexts: list[ChunkTextsModel] = []
        chunksQuestions: list[ChunkQuestionsModel] = []
        chunkClaims: list[ChunkClaimsModel] = []
        start = 0
        while start < len(chunks):
            print(f"{start} of {len(chunks)}")
            chunkClaimQuesResponse: (
                ExtractClaimsAndQuestionsFromChunkResponseModel | None
            ) = None

            try:
                LLMChunkRelationMessages: list[ChatServiceMessageModel] = [
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.SYSTEM,
                        content=ExtractClaimsAndQuestionsFromChunkSystemPrompt,
                    ),
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.USER,
                        content=chunks[start],
                    ),
                ]
                chunkClaimQuesResponse = await self.ExtractClaimsAndQuesFromChunk(
                    messages=LLMChunkRelationMessages,
                    retryLoopIndex=0,
                )
                chunkId = uuid4()
                chunkTexts.append(
                    ChunkTextsModel(id=chunkId, text=chunkClaimQuesResponse.chunk)
                )
                chunksQuestions.append(
                    ChunkQuestionsModel(
                        chunkId=chunkId, questions=chunkClaimQuesResponse.questions
                    )
                )
                chunkClaims.append(
                    ChunkClaimsModel(
                        chunkId=chunkId, claims=chunkClaimQuesResponse.claims
                    )
                )

            except Exception as e:
                print(f"Error processing chunk at index {start}: {e}")
                start = start
                continue

            vecTexts: list[str] = []
            vecTexts.append(chunkClaimQuesResponse.chunk)

            for question in chunkClaimQuesResponse.questions:
                vecTexts.append(question)
            for claim in chunkClaimQuesResponse.claims:
                vecTexts.append(claim)

            vecResp = await self.ConvertTextsToVectors(retryLoopIndex=0, texts=vecTexts)

            queLen = len(chunkClaimQuesResponse.questions)
            claimsLen = len(chunkClaimQuesResponse.claims)

            if vecResp.data is not None:
                for index, item in enumerate(vecResp.data):
                    if index == 0:
                        chunkTexts[start].embedding = item.embedding
                    else:
                        chunksQuestions[start].questionEmbeddings = cast(
                            Any,
                            [item.embedding for item in vecResp.data[1 : queLen + 1]],
                        )

                        chunkClaims[start].ClaimEmbeddings = cast(
                            Any,
                            [
                                item.embedding
                                for item in vecResp.data[
                                    1 + queLen : queLen + 1 + claimsLen
                                ]
                            ],
                        )

        return BuildRagFromDocResponseModel(
            chunkClaims=chunkClaims,
            chunkQuestion=chunksQuestions,
            chunkTexts=chunkTexts,
        )

    async def BuildRagFromDoc(self, file: str) -> BuildRagFromDocResponseModel:
        chunksRelations: BuildRagFromDocResponseModel = (
            await self.HandleEmbeddingsConversion(file)
        )

        return chunksRelations
