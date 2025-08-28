import re
import unicodedata
from typing import Any, Tuple, cast
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
    RerankingRequestModel,
    RerankingResponseModel,
    FindTopKresultsFromVectorsRequestModel,
    EmbeddingResponseModel,
)
from ragservices.implementations import BuildGraphFromDocServiceImpl_Rag
from utils import ExtractTextFromDoc_Rag
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ragservices.utils.BuildGraphFromDocSystemPrompts_Rag import (
    ExtractRealtionsAndQuestionsFromChunkSystemPrompt_Rag,
    ExtractImageIndexFromChunkSystemPrompt_Rag,
)
import json
from ragservices.models import (
    ChunkRelationsModel_Rag,
    CHunkTextsModel_Rag,
    ChunkRelationModel_Rag,
    GetGraphFromDocResponseModel_Rag,
    ChunkMatchedNodeModel_Rag,
    ChunkImagesModel_Rag,
    ExtarctRelationsAndQuestionFromChunkResponseModel_Rag,
    ExatrctImageIndexFromChunkSectionModel_Rag,
    ExatrctImageIndexFromChunkResponseModel_Rag,
)
from uuid import UUID, uuid4

import base64
import firebase_admin
from firebase_admin import credentials, storage
import time

chatService = ChatService()
embeddingService = EmbeddingService()
rerankingService = RerankingService()

cred = credentials.Certificate("./others/firebaseCred.json")
cast(Any, firebase_admin).initialize_app(
    cred, {"storageBucket": "testproject-b1efd.appspot.com"}
)


RetryLoopIndexLimit = 3


class BuildGraphFromDocService_Rag(BuildGraphFromDocServiceImpl_Rag):

    def ExtractChunksFromDoc_Rag(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> Tuple[list[str], list[str]]:
        _PAGE_RE = re.compile(r"\bpage\s+\d+\s+of\s+\d+\b", re.IGNORECASE)
        _IMAGE_RE = re.compile(r"\s*(<<IMAGE-\d+>>)\s*", re.IGNORECASE)
        _BULLET_LINE_RE = re.compile(r"^[\s•\-\*\u2022\uf0b7FÞ]+(?=\S)", re.MULTILINE)
        _SOFT_HYPHEN_RE = re.compile(r"\u00AD")
        _HYPHEN_BREAK_RE = re.compile(r"(\w)-\n(\w)")
        _MULTI_NL_RE = re.compile(r"\n{3,}")
        _WS_NL_RE = re.compile(r"[ \t]+\n")
        _WS_RUN_RE = re.compile(r"[ \t]{2,}")

        def _normalizeText(raw: str) -> str:
            t = unicodedata.normalize("NFKC", raw)
            t = _SOFT_HYPHEN_RE.sub("", t)
            t = _PAGE_RE.sub(" ", t)
            t = _BULLET_LINE_RE.sub("", t)
            t = _HYPHEN_BREAK_RE.sub(r"\1\2", t)
            t = _IMAGE_RE.sub(r" \1 ", t)
            t = _WS_NL_RE.sub("\n", t)
            t = _MULTI_NL_RE.sub("\n\n", t)
            t = _WS_RUN_RE.sub(" ", t)
            t = re.sub(r"\s+", " ", t)
            return t.strip()

        def _mergeTinyChunks(chunks: list[str], minChars: int) -> list[str]:
            merged: list[str] = []
            carry = ""
            for ch in chunks:
                chs = ch.strip()
                if not chs:
                    continue
                if _IMAGE_RE.fullmatch(chs) or len(chs) < minChars:
                    if merged:
                        merged[-1] = (merged[-1].rstrip() + " " + chs).strip()
                    else:
                        carry = (carry + " " + chs).strip()
                else:
                    if carry:
                        chs = (carry + " " + chs).strip()
                        carry = ""
                    merged.append(chs)
            if carry:
                if merged:
                    merged[-1] = (merged[-1].rstrip() + " " + carry).strip()
                else:
                    merged = [carry]
            return merged

        text, images = ExtractTextFromDoc_Rag(file)
        text = _normalizeText(text)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunkSize,
            chunk_overlap=chunkOLSize or 0,
            separators=["\n\n", "\n", " "],
            is_separator_regex=False,
            length_function=len,
        )
        chunks = splitter.split_text(text)
        chunks = _mergeTinyChunks(chunks, minChars=max(200, chunkSize // 3))
        return (
            chunks,
            images,
        )

    async def UploadImagesFromDocToFirebase_Rag(
        self, base64Str: str, folder: str
    ) -> str:
        imageBytes: bytes = base64.b64decode(base64Str)
        filename: str = f"{folder}/{uuid4()}.png"
        bucket: Any = cast(Any, storage).bucket()
        blob: Any = bucket.blob(filename)
        blob.upload_from_string(imageBytes, content_type="image/png")
        blob.make_public()
        publicUrl: str = cast(str, blob.public_url)
        return publicUrl

    async def ConvertTextsToVectorsFromChunk_Rag(
        self, texts: list[str], retryLoopIndex: int
    ) -> EmbeddingResponseModel:
        if retryLoopIndex > RetryLoopIndexLimit:
            raise Exception("Exception while converting texts to vector")

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
        if retryLoopIndex > RetryLoopIndexLimit:
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
                                        "entities": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                            type="array",
                                            items={"type": "string"},
                                        ),
                                        "relations": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                            type="array",
                                            items={"type": "string"},
                                        ),
                                        "questions": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                            type="array",
                                            items={"type": "string"},
                                        ),
                                        "relationshipsEntities": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                            type="array",
                                            items={
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                        ),
                                        "chunk": ChatServiceCerebrasFormatJsonSchemaJsonSchemaPropertyModel(
                                            type="string"
                                        ),
                                    },
                                    required=[
                                        "entities",
                                        "relations",
                                        "relationshipsEntities",
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
            if len(LLMResponse.get("relations")) != len(
                LLMResponse.get("relationshipsEntities")
            ):
                messages.append(
                    ChatServiceMessageModel(
                        role=ChatServiceMessageRoleEnum.USER,
                        content="relations and relationshipsEntities length must be same ",
                    )
                )

                await self.ExtarctRelationsAndQuestionFromChunk_Rag(
                    messages=messages,
                    retryLoopIndex=0,
                )

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
            entities=LLMResponse.get("entities"),
            questions=LLMResponse.get("questions"),
            realtions=LLMResponse.get("relations"),
            relationshipsEntities=LLMResponse.get("relationshipsEntities"),
        )
        return response

    async def ExatrctImageIndexFromChunk_Rag(
        self,
        messages: list[ChatServiceMessageModel],
        chunkText: str,
        retryLoopIndex: int,
    ) -> ExatrctImageIndexFromChunkResponseModel_Rag:
        if retryLoopIndex > RetryLoopIndexLimit:
            raise Exception("Exception while extarcting image index from chunk")

        if not (re.search(r"<<\s*image-\d+\s*>>", chunkText, flags=re.IGNORECASE)):
            return ExatrctImageIndexFromChunkResponseModel_Rag(sections=[])

        LLMImageExtractResponse: Any = await chatService.Chat(
            modelParams=ChatServiceRequestModel(
                apiKey=GetCerebrasApiKey(),
                model="qwen-3-32b",
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
        chunks, images = self.ExtractChunksFromDoc_Rag(file, 600)
        chunkTexts: list[CHunkTextsModel_Rag] = []
        chunksRealtions: list[ChunkRelationsModel_Rag] = []

        for start in range(0, len(chunks), 1):
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
            LLMChunkImagesMessages: list[ChatServiceMessageModel] = [
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.SYSTEM,
                    content=ExtractImageIndexFromChunkSystemPrompt_Rag,
                ),
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content=chunks[start],
                ),
            ]
            chunkImageResponse = await self.ExatrctImageIndexFromChunk_Rag(
                retryLoopIndex=0,
                messages=LLMChunkImagesMessages,
                chunkText=chunks[start],
            )

            chunkId = uuid4()
            chunkTexts.append(
                CHunkTextsModel_Rag(
                    id=chunkId,
                    text=chunksRelationsResponse.chunk,
                    entities=chunksRelationsResponse.entities,
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
                        imageUrl = await self.UploadImagesFromDocToFirebase_Rag(
                            base64Str=image, folder="opdImages"
                        )
                        image = imageUrl
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
            for relation, relationEntities in zip(
                chunksRelationsResponse.realtions,
                chunksRelationsResponse.relationshipsEntities,
            ):
                chunkRelations.append(
                    ChunkRelationModel_Rag(
                        realtion=relation,
                        realtionEntites=relationEntities,
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
            zipped = list(
                zip(
                    chunksRelationsResponse.realtions,
                    chunksRelationsResponse.relationshipsEntities,
                )
            )
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

        return GetGraphFromDocResponseModel_Rag(
            chunkTexts=chunkTexts, chunkRelations=chunksRealtions
        )

    async def BuildGraphFromDoc_Rag(
        self, file: str
    ) -> GetGraphFromDocResponseModel_Rag:
        chunksRelations: GetGraphFromDocResponseModel_Rag = (
            await self.ExtractChunksAndRelationsFromDoc_Rag(file)
        )

        chunkVectors = [chunk.vector for chunk in chunksRelations.chunkTexts]

        for index, vector in enumerate(chunkVectors):
            sourceVectors: list[list[float]] = []
            for index1, vec in enumerate(chunkVectors):
                if index != index1:
                    sourceVectors.append(cast(list[float], vec))

            topResultsFromFaiss = rerankingService.FindTopKResultsFromVectors(
                request=FindTopKresultsFromVectorsRequestModel(
                    queryVector=cast(list[float], vector),
                    topK=20,
                    sourceVectors=sourceVectors,
                )
            )
            docs: list[str] = []
            docsIds: list[UUID] = []
            if topResultsFromFaiss.indeces is not None:
                for index2 in topResultsFromFaiss.indeces:
                    if index2 != -1 and index2 != index:
                        docs.append(chunksRelations.chunkTexts[index2].text)
                        docsIds.append(chunksRelations.chunkTexts[index2].id)

            response: RerankingResponseModel = await rerankingService.FindRankingScore(
                RerankingRequestModel(
                    model="jina-reranker-m0",
                    query=chunksRelations.chunkTexts[index].text,
                    docs=docs,
                    topN=10,
                )
            )
            matchedNodes: list[ChunkMatchedNodeModel_Rag] = []
            if response.response is not None:
                for res in response.response:
                    if res.score > 0.9:
                        matchedNodes.append(
                            ChunkMatchedNodeModel_Rag(
                                chunkId=docsIds[res.index],
                                score=res.score,
                            )
                        )
            if len(matchedNodes) > 0:
                chunksRelations.chunkTexts[index].matchedNodes = matchedNodes
        return chunksRelations
