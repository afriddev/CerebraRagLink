import re
import unicodedata
from typing import Any, cast
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
)
from graphrag.implementations import FileChunkGragImpl
from utils import ExtractTextFromDoc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from graphrag.utils.GragSystemPropts import ExtractEntityGragSystemPrompt
import json
from graphrag.models import (
    ChunkRelationsModel,
    ChunkTextsModel,
    ChunkRelationModel,
    HandleKgExatrctProcessResponseModel,
)
from uuid import uuid4

chatService = ChatService()
embeddingService = EmbeddingService()
rerankingService = RerankingService()


class FileChunkGragService(FileChunkGragImpl):

    def ExatrctChunkFromText(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> list[str]:
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

        text = ExtractTextFromDoc(file)
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
        return chunks

    async def HandleRelationExtarctProcess(self, file: str):
        chunks = self.ExatrctChunkFromText(file, 600)
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
                    temperature=0.4,
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
                )
            )
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

        batchSize = 5
        for index in range(0, len(chunkTexts), batchSize):
            chunkTextsBatch = [
                chunk.text for chunk in chunkTexts[index : index + batchSize]
            ]
            chunkRelationsBatch = [
                relation.realtion
                for relations in chunkRealtions[index : index + batchSize]
                for relation in relations.chunkRelations
            ]
            chunkTextsEmbeddingResponse = await embeddingService.ConvertTextToEmbedding(
                chunkTextsBatch
            )
            relationsEmbeddingResponse = await embeddingService.ConvertTextToEmbedding(
                chunkRelationsBatch
            )
            if chunkTextsEmbeddingResponse.data is not None:
                for index2, vector in enumerate(chunkTextsEmbeddingResponse.data):
                    chunkTexts[cast(int, vector.index) + index2].vector = (
                        vector.embedding
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

        return HandleKgExatrctProcessResponseModel(
            chunkTexts=chunkTexts, chunkRelations=chunkRealtions
        )

    async def HandleGraphBuildingProcess(self, file: str):
        relations: HandleKgExatrctProcessResponseModel = (
            await self.HandleRelationExtarctProcess(file)
        )

        for index in range(0, 1):
            await rerankingService.FindRankingScore(
                RerankingRequestModel(
                    model="Salesforce/Llama-Rank-v1",
                    query=relations.chunkTexts[index].text,
                    docs=[chunk.text for chunk in relations.chunkTexts],
                    topN=len(relations.chunkTexts),
                )
            )
