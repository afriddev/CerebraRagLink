import re
import unicodedata
from typing import Any, Tuple, cast
from clientservices import (
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
from graphrag.implementations import FileChunkGragImpl
from utils import ExtractTextFromDoc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from graphrag.utils.FileGragSystemPropts import ExtractEntityGragSystemPrompt
import json
from graphrag.models import (
    ChunkRelationsModel,
    ChunkTextsModel,
    ChunkRelationModel,
    HandleChunkRelationExtractResponseModel,
    ChunkNodeModel,
    ChunkImagesData,
)
from uuid import UUID, uuid4

import base64
import firebase_admin
from firebase_admin import credentials, storage


chatService = ChatService()
embeddingService = EmbeddingService()
rerankingService = RerankingService()

cred = credentials.Certificate("./others/firebaseCred.json")
firebase_admin.initialize_app(cred, {"storageBucket": "testproject-b1efd.appspot.com"})


class FileChunkGragService(FileChunkGragImpl):

    def ExatrctChunkFromText(
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

        text, images = ExtractTextFromDoc(file)
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

    async def UplaodFileToFirebaseStorage(self, base64Str: str, folder: str) -> str:
        imageBytes: bytes = base64.b64decode(base64Str)
        filename: str = f"{folder}/{uuid4()}.png"
        bucket: Any = cast(Any, storage.bucket())
        blob: Any = bucket.blob(filename)
        blob.upload_from_string(imageBytes, content_type="image/png")
        blob.make_public()
        publicUrl: str = cast(str, blob.public_url)
        return publicUrl

    async def HandleKgChunkRelationExtarctProcess(self, file: str):
        chunks, images = self.ExatrctChunkFromText(file, 600)
        chunkTexts: list[ChunkTextsModel] = []
        chunkRealtions: list[ChunkRelationsModel] = []

        for start in range(0, 10, 1):
            messages: list[ChatServiceMessageModel] = [
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.USER,
                    content=chunks[start],
                ),
                ChatServiceMessageModel(
                    role=ChatServiceMessageRoleEnum.SYSTEM,
                    content=ExtractEntityGragSystemPrompt,
                ),
            ]
            LLMResponse: Any = await chatService.Chat(
                modelParams=ChatServiceRequestModel(
                    apiKey=GetCerebrasApiKey(),
                    model="qwen-3-235b-a22b-instruct-2507",
                    maxCompletionTokens=30000,
                    messages=messages,
                    temperature=0.2,
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
                                                    "required": [
                                                        "number",
                                                        "title",
                                                        "description",
                                                    ],
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
                ChunkTextsModel(
                    id=chunkId,
                    text=chunkResponse.get("chunk"),
                    entities=chunkResponse.get("entities"),
                    questions=chunkResponse.get("questions"),
                )
            )

            imageData: list[ChunkImagesData] = []

            for imgData in chunkResponse.get("sections"):
                image = ""
                imagePlaceholder = imgData.get("image")
                if imagePlaceholder != "":
                    imageIndex = int(re.sub(r"\D", "", imagePlaceholder)) - 1

                    image = images[imageIndex]
                    imageUrl = await self.UplaodFileToFirebaseStorage(
                        base64Str=image, folder="opdImages"
                    )
                    image = imageUrl
                imageData.append(
                    ChunkImagesData(
                        description=imgData.get("description"),
                        image=image,
                        sectionNumber=float(imgData.get("number")),
                        title=imgData.get("title"),
                    )
                )
            chunkTexts[start].images = imageData

            chunkRelations: list[ChunkRelationModel] = []
            for relation, relationEntities in zip(
                chunkResponse.get("relations"),
                chunkResponse.get("relationshipsEntities"),
            ):
                chunkRelations.append(
                    ChunkRelationModel(
                        realtion=relation,
                        realtionEntites=relationEntities,
                        id=uuid4(),
                    )
                )
            chunkRealtions.append(
                ChunkRelationsModel(chunkId=chunkId, chunkRelations=chunkRelations)
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

        return HandleChunkRelationExtractResponseModel(
            chunkTexts=chunkTexts, chunkRelations=chunkRealtions
        )

    async def HandleChunksGraphBuildingProcess(
        self, file: str
    ) -> HandleChunkRelationExtractResponseModel:
        chunksRelations: HandleChunkRelationExtractResponseModel = (
            await self.HandleKgChunkRelationExtarctProcess(file)
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
            matchedNodes: list[ChunkNodeModel] = []
            if response.response is not None:
                for res in response.response:
                    if res.score > 0.9:
                        matchedNodes.append(
                            ChunkNodeModel(
                                chunkId=docsIds[res.index],
                                score=res.score,
                            )
                        )
            if len(matchedNodes) > 0:
                chunksRelations.chunkTexts[index].matchedNodes = matchedNodes
        return chunksRelations
