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
)
from ragservices.implementations import BuildGraphFromDocServiceImpl_Rag
from utils import ExtractTextFromDoc_Rag
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ragservices.utils.BuildGraphFromDocSystemPrompts_Rag import (
    ExtractEntityGragSystemPrompt,
)
import json
from ragservices.models import (
    ChunkRelationsModel_Rag,
    CHunkTextsModel_Rag,
    ChunkRelationModel_Rag,
    GetGraphFromDocResponseModel_Rag,
    ChunkMatchedNodeModel_Rag,
    ChunkImagesModel_Rag,
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
firebase_admin.initialize_app(cred, {"storageBucket": "testproject-b1efd.appspot.com"})


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
        bucket: Any = cast(Any, storage.bucket())
        blob: Any = bucket.blob(filename)
        blob.upload_from_string(imageBytes, content_type="image/png")
        blob.make_public()
        publicUrl: str = cast(str, blob.public_url)
        return publicUrl

    def StrToFloat(self, numberText: Any):
        if numberText is None:
            return None
        rawNumber = str(numberText).strip()
        cleanedNumber = re.sub(r"[^0-9.]", "", rawNumber)
        if not cleanedNumber:
            return None
        if not re.fullmatch(r"\d+(?:\.\d+)*", cleanedNumber):
            return None
        normalizedNumber = re.sub(r"\.(?=.*\.)", "", cleanedNumber)
        try:
            return float(normalizedNumber)
        except Exception:
            return None

    async def ExtractChunksAndRelationsFromDoc_Rag(self, file: str):
        chunks, images = self.ExtractChunksFromDoc_Rag(file, 600)
        chunkTexts: list[CHunkTextsModel_Rag] = []
        chunkRealtions: list[ChunkRelationsModel_Rag] = []

        for start in range(0, len(chunks), 1):
            messages: list[ChatServiceMessageModel] = [
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.SYSTEM,
                    content=ExtractEntityGragSystemPrompt,
                ),
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content=chunks[start],
                ),
            ]
            time.sleep(1)
            LLMResponse: Any = await chatService.Chat(
                modelParams=ChatServiceRequestModel(
                    apiKey=GetCerebrasApiKey(),
                    model="qwen-3-32b",
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
                                            "sections": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "number": {"type": "string"},
                                                        "title": {"type": "string"},
                                                        "image": {"type": "string"},
                                                        "description": {
                                                            "type": "string"
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                        required=[
                                            "entities",
                                            "relations",
                                            "relationshipsEntities",
                                            "chunk",
                                            "questions",
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
            chunkResponse = json.loads(
                LLMResponse.LLMData.choices[0].message.content
            ).get("response")
            chunkId = uuid4()
            chunkTexts.append(
                CHunkTextsModel_Rag(
                    id=chunkId,
                    text=chunkResponse.get("chunk"),
                    entities=chunkResponse.get("entities"),
                    questions=chunkResponse.get("questions"),
                )
            )

            imageData: list[ChunkImagesModel_Rag] = []

            for imgData in chunkResponse.get("sections"):
                image = ""
                imagePlaceholder = imgData.get("image")
                imageTagRegex = re.compile(r"^<<\s*image-(\d+)\s*>>$", re.IGNORECASE)
                m = None
                if imagePlaceholder is not None:
                    m = imageTagRegex.match(imagePlaceholder)
                print(imgData.get("image"),imgData.get("number"))
                if (
                    imagePlaceholder is not None
                    and imagePlaceholder != ""
                    and self.StrToFloat(imgData.get("number")) is not None
                    and m
                    and imgData.get("title") is not None
                    and imgData.get("description") is not None
                    and imgData.get("description") != ""
                    and imgData.get("title") != ""
                ):
                    imageIndex = int(re.sub(r"\D", "", imagePlaceholder)) - 1

                    try:
                        image = images[imageIndex]
                        imageUrl = await self.UploadImagesFromDocToFirebase_Rag(
                            base64Str=image, folder="opdImages"
                        )
                        image = imageUrl
                        imageData.append(
                            ChunkImagesModel_Rag(
                                description=imgData.get("description"),
                                image=image,
                                sectionNumber=cast(
                                    Any, self.StrToFloat(imgData.get("number"))
                                ),
                                title=imgData.get("title"),
                            )
                        )
                    except Exception as e:
                        print(imgData.get("number"))
                        print(f"Error parsing section number: {e}")

            chunkTexts[start].images = imageData

            chunkRelations: list[ChunkRelationModel_Rag] = []
            for relation, relationEntities in zip(
                chunkResponse.get("relations"),
                chunkResponse.get("relationshipsEntities"),
            ):
                chunkRelations.append(
                    ChunkRelationModel_Rag(
                        realtion=relation,
                        realtionEntites=relationEntities,
                        id=uuid4(),
                    )
                )

            chunkRealtions.append(
                ChunkRelationsModel_Rag(chunkId=chunkId, chunkRelations=chunkRelations)
            )

        batchSize = 15
        for index in range(0, len(chunkTexts), batchSize):
            chunkTextsBatch = [
                chunk.text for chunk in chunkTexts[index : index + batchSize]
            ]

            chunkQuestionsBatch = [
                question
                for chunkQuestions in chunkTexts[index : index + batchSize]
                for question in chunkQuestions.questions
            ]

            chunkRelationsBatch = [
                relation.realtion
                for relations in chunkRealtions[index : index + batchSize]
                for relation in relations.chunkRelations
            ]
            chunkTextsEmbeddingResponse = await embeddingService.ConvertTextToEmbedding(
                chunkTextsBatch
            )

            chunkQuestionsEmbeddingResponse = (
                await embeddingService.ConvertTextToEmbedding(chunkQuestionsBatch)
            )

            relationsEmbeddingResponse = await embeddingService.ConvertTextToEmbedding(
                chunkRelationsBatch
            )
            if chunkTextsEmbeddingResponse.data is not None:
                for _, vector in enumerate(chunkTextsEmbeddingResponse.data):
                    chunkTexts[index + cast(int, vector.index)].vector = (
                        vector.embedding
                    )

            if chunkQuestionsEmbeddingResponse.data is not None:
                for index4, _ in enumerate(chunkTexts[index : index + batchSize]):
                    for index5, _ in enumerate(chunkTexts[index4].questions):
                        cast(Any, chunkTexts[index + index4].questionVectors).append(
                            cast(
                                Any,
                                chunkQuestionsEmbeddingResponse.data[
                                    index4 + index5
                                ].embedding,
                            )
                        )

            if relationsEmbeddingResponse.data is not None:
                for index3, chunkRelation in enumerate(
                    chunkRealtions[index : index + batchSize]
                ):
                    for index4, _ in enumerate(chunkRelation.chunkRelations):
                        chunkRealtions[index + index3].chunkRelations[
                            index4
                        ].relationVector = relationsEmbeddingResponse.data[
                            index3 + index4
                        ].embedding

        return GetGraphFromDocResponseModel_Rag(
            chunkTexts=chunkTexts, chunkRelations=chunkRealtions
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
