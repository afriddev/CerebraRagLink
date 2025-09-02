import re
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
from ragservices.implementations import BuildRagFromDocServiceImpl_Rag
from ragservices.utils.BuildRagFromDocSystemPrompts_Rag import (
    ExtractRealtionsAndQuestionsFromChunkSystemPrompt_Rag,
    ExtractImageIndexFromChunkSystemPrompt_Rag,
)
import json
from ragservices.models import (
    ChunkRelationsModel_Rag,
    CHunkTextsModel_Rag,
    ChunkRelationModel_Rag,
    GetRagFromDocResponseModel_Rag,
    ChunkImagesModel_Rag,
    ExtarctRelationsAndQuestionFromChunkResponseModel_Rag,
    ExatrctImageIndexFromChunkSectionModel_Rag,
    ExatrctImageIndexFromChunkResponseModel_Rag,
)
from uuid import uuid4
import time
from ragservices.services.RagUtilServcies_Rag import RagUtilService_Rag


chatService = ChatService()
embeddingService = EmbeddingService()
rerankingService = RerankingService()
RagUtilService = RagUtilService_Rag()


class BuildRagFromDocService_Rag(BuildRagFromDocServiceImpl_Rag):

    def __init__(self):
        self.RetryLoopIndexLimit = 3

    async def ConvertTextsToVectorsFromChunk_Rag(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        if retryLoopIndex > self.RetryLoopIndexLimit:
            return EmbeddingResponseModel(status=EmbeddingResponseEnum.ERROR)

        embeddingResponse = await embeddingService.ConvertTextToEmbedding(text=texts)
        if embeddingResponse.data is None:
            await self.ConvertTextsToVectorsFromChunk_Rag(
                texts=texts, retryLoopIndex=retryLoopIndex + 1
            )
        return embeddingResponse

    async def ExtarctRelationsAndQuestionFromChunk_Rag(
        self,
        messages: list[ChatServiceMessageModel],
        retryLoopIndex: int,
    ) -> ExtarctRelationsAndQuestionFromChunkResponseModel_Rag:
        if retryLoopIndex > self.RetryLoopIndexLimit:
            raise Exception(
                "Exception while extarcting relation and questions from chunk"
            )

        LLMChunksRelationsExtractResponse: Any = await chatService.Chat(
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
                                        "relations": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
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
                                        "relations",
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
                LLMChunksRelationsExtractResponse.LLMData.choices[0].message.content
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

            await self.ExtarctRelationsAndQuestionFromChunk_Rag(
                messages=messages,
                retryLoopIndex=retryLoopIndex + 1,
            )
            
            
        response = ExtarctRelationsAndQuestionFromChunkResponseModel_Rag(
            chunk=LLMResponse.get("chunk"),
            questions=LLMResponse.get("questions"),
            realtions=LLMResponse.get("relations"),
        )
        return response

    async def ExatrctImageIndexFromChunk_Rag(
        self,
        messages: list[ChatServiceMessageModel],
        chunkText: str,
        retryLoopIndex: int,
    ) -> ExatrctImageIndexFromChunkResponseModel_Rag:
        if retryLoopIndex > self.RetryLoopIndexLimit:
            raise Exception("Exception while extarcting image index from chunk")

        if not (re.search(r"<<\s*image-\d+\s*>>", chunkText, flags=re.IGNORECASE)):
            return ExatrctImageIndexFromChunkResponseModel_Rag(sections=[])

        LLMImageExtractResponse: Any = await chatService.Chat(
            modelParams=ChatServiceRequestModel(
                apiKey=GetCerebrasApiKey(),
                model="llama-4-maverick-17b-128e-instruct",
                maxCompletionTokens=3000,
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
                                        "sections": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "imageindex": {"type": "string"},
                                                    "description": {"type": "string"},
                                                },
                                            },
                                        },
                                    },
                                    required=[
                                        "sections",
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
                LLMImageExtractResponse.LLMData.choices[0].message.content
            ).get("response")
        except Exception as e:
            print("Error occured while extracting image index from chunk retrying ...")
            print(e)
            messages.append(
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content="Please generate a valid json object",
                )
            )
            await self.ExatrctImageIndexFromChunk_Rag(
                messages=messages,
                chunkText=chunkText,
                retryLoopIndex=retryLoopIndex + 1,
            )
        imageSections: list[ExatrctImageIndexFromChunkSectionModel_Rag] = []

        if LLMResponse.get("sections") is not None:
            for section in LLMResponse.get("sections"):
                try:
                    imageSections.append(
                        ExatrctImageIndexFromChunkSectionModel_Rag(
                            description=section.get("description"),
                            imageindex=int(re.sub(r"\D", "", section.get("imageindex")))
                            - 1,
                        )
                    )
                except:
                    imageSections.append(
                        ExatrctImageIndexFromChunkSectionModel_Rag(
                            description=section.get("description"),
                            imageindex=None,
                        )
                    )

        return ExatrctImageIndexFromChunkResponseModel_Rag(sections=imageSections)

    async def ExtractChunksAndRelationsFromDoc_Rag(self, file: str):
        chunks, images = RagUtilService.ExtractChunksFromDoc_Rag(file, 600)
        chunkTexts: list[CHunkTextsModel_Rag] = []
        chunksRealtions: list[ChunkRelationsModel_Rag] = []
        start = 0
        while start < len(chunks):
            print(f"{start} of {len(chunks)}")
            chunksRelationsResponse: (
                ExtarctRelationsAndQuestionFromChunkResponseModel_Rag | None
            ) = None
            chunkImageResponse: ExatrctImageIndexFromChunkResponseModel_Rag | None = (
                None
            )

            try:
                time.sleep(1)
                LLMChunkRelationMessages: list[ChatServiceMessageModel] = [
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.SYSTEM,
                        content=ExtractRealtionsAndQuestionsFromChunkSystemPrompt_Rag,
                    ),
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.USER,
                        content=chunks[start],
                    ),
                ]
                chunksRelationsResponse = (
                    await self.ExtarctRelationsAndQuestionFromChunk_Rag(
                        messages=LLMChunkRelationMessages,
                        retryLoopIndex=0,
                    )
                )
                time.sleep(1)
                _IMAGE_TOKEN_RE = re.compile(r"<<\s*image-\d+\s*>>", re.IGNORECASE)
                prevChunk = (
                    "" if start == 0 else _IMAGE_TOKEN_RE.sub("", chunks[start - 1])
                )
                nextChunk = (
                    ""
                    if start == len(chunks) - 1
                    else _IMAGE_TOKEN_RE.sub("", chunks[start + 1])
                )

                LLMChunkImagesMessages: list[ChatServiceMessageModel] = [
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.SYSTEM,
                        content=ExtractImageIndexFromChunkSystemPrompt_Rag,
                    ),
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.USER,
                        content=json.dumps(
                            {
                                "mainchunk": chunks[start],
                                "previouschunk": prevChunk,
                                "nextchunk": nextChunk,
                            }
                        ),
                    ),
                ]

                chunkImageResponse = await self.ExatrctImageIndexFromChunk_Rag(
                    retryLoopIndex=0,
                    messages=LLMChunkImagesMessages,
                    chunkText=chunks[start],
                )
            except Exception as e:
                print(f"Error processing chunk at index {start}: {e}")
                start = start
                continue

            chunkId = uuid4()
            chunkTexts.append(
                CHunkTextsModel_Rag(
                    id=chunkId,
                    text=chunksRelationsResponse.chunk,
                    questions=chunksRelationsResponse.questions,
                )
            )

            imageData: list[ChunkImagesModel_Rag] = []

            for imgData in chunkImageResponse.sections:
                image = ""
                imageIndex = imgData.imageindex
                if imageIndex is not None:

                    try:
                        image = images[imageIndex]
                        imageUrl = (
                            await RagUtilService.UploadImagesFromDocToFirebase_Rag(
                                base64Str=image, folder="opdImages"
                            )
                        )
                        image = imageUrl
                        print(imageIndex)
                        print(imgData.description)
                        imageData.append(
                            ChunkImagesModel_Rag(
                                description=imgData.description,
                                image=image,
                            )
                        )
                    except Exception as e:
                        print(f"Error parsing section: {e}")

            chunkTexts[start].images = imageData

            chunkRelations: list[ChunkRelationModel_Rag] = []
            for relation in chunksRelationsResponse.realtions:
                chunkRelations.append(
                    ChunkRelationModel_Rag(
                        realtion=relation,
                        id=uuid4(),
                    )
                )

            texts: list[str] = []
            texts.append(chunksRelationsResponse.chunk)
            for _, question in enumerate(chunksRelationsResponse.questions):
                texts.append(question)
            for _, relation in enumerate(chunksRelationsResponse.realtions):
                texts.append(relation)

            textVectors = await self.ConvertTextsToVectorsFromChunk_Rag(
                texts=texts, retryLoopIndex=0
            )
            c = 1
            qLen = len(chunksRelationsResponse.questions)
            zipped = list(zip(chunksRelationsResponse.realtions))
            rLen = len(zipped)
            if textVectors.data is not None:
                chunkTexts[start].vector = textVectors.data[0].embedding
                qVectors: list[list[float]] = []
                for qIndex in range(c, c + qLen):
                    qVectors.append(cast(Any, textVectors).data[qIndex].embedding)
                chunkTexts[start].questionVectors = qVectors

                for rIndex in range(
                    c + qLen,
                    c + qLen + rLen,
                ):
                    chunkRelations[rIndex - (c + qLen)].relationVector = (
                        textVectors.data[rIndex].embedding
                    )

            chunksRealtions.append(
                ChunkRelationsModel_Rag(chunkId=chunkId, chunkRelations=chunkRelations)
            )
            start += 1

        return GetRagFromDocResponseModel_Rag(
            chunkTexts=chunkTexts, chunkRelations=chunksRealtions
        )

    async def BuildRagFromDoc_Rag(self, file: str) -> GetRagFromDocResponseModel_Rag:
        chunksRelations: GetRagFromDocResponseModel_Rag = (
            await self.ExtractChunksAndRelationsFromDoc_Rag(file)
        )

        return chunksRelations
