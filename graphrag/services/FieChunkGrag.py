import re
import unicodedata
from typing import Any
from clientservices import (
    LLMResponseFormatJsonSchemaSchemaModel,
    LLMService,
    LLMRequestModel,
    GetCerebrasApiKey,
    LLMResponseFormatModel,
    LLmresponseFormatJsonSchemaModel,
    LLMResponseFormatPropertySchemaModel,
    LLMMessageModel,
    LLmMessageRoleEnum,
)
from graphrag.implementations import FileChunkGragImpl
from utils import ExtractTextFromDoc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from graphrag.utils.GragSystemPropts import ExtractEntityGragSystemPrompt


llmService = LLMService()


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

    async def handleEntitiesProcess(self, file: str):
        chunks = self.ExatrctChunkFromText(file, 1000)
        for start in range(3, 5):
            messages: list[LLMMessageModel] = [
                LLMMessageModel(
                    role=LLmMessageRoleEnum.SYSTEM,
                    content=ExtractEntityGragSystemPrompt,
                ),
                LLMMessageModel(
                    role=LLmMessageRoleEnum.USER,
                    content=chunks[start],
                ),
            ]

            LLMResponse: Any = await llmService.Chat(
                modelParams=LLMRequestModel(
                    apiKey=GetCerebrasApiKey(),
                    model="qwen-3-32b",
                    maxCompletionTokens=10000,
                    messages=messages,
                    temperature=0.7,
                    responseFormat=LLMResponseFormatModel(
                        type="json_schema",
                        jsonSchema=LLmresponseFormatJsonSchemaModel(
                            name="schema",
                            strict=True,
                            jsonSchema=LLMResponseFormatJsonSchemaSchemaModel(
                                type="object",
                                properties={
                                    "response": LLMResponseFormatPropertySchemaModel(
                                        type="object",
                                        properties={
                                            "entities": LLMResponseFormatPropertySchemaModel(
                                                type="array",
                                                items={"type": "string"},
                                            ),
                                            "relations": LLMResponseFormatPropertySchemaModel(
                                                type="array",
                                                items={"type": "string"},
                                            ),
                                            "relationshipsEntities": LLMResponseFormatPropertySchemaModel(
                                                type="array",
                                                items={
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            ),
                                            "chunk": LLMResponseFormatPropertySchemaModel(
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

            print(LLMResponse.LLMData.choices[0].message.content)
