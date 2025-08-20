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
import json


llmService = LLMService()


class FileChunkGragService(FileChunkGragImpl):

    def ExatrctChunkFromText(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> list[str]:
        text = ExtractTextFromDoc(file)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunkSize, chunk_overlap=chunkOLSize
        )
        chunks = splitter.split_text(text)
        return chunks

    async def handleEntitiesProcess(self, file: str):
        chunks = self.ExatrctChunkFromText(file, 500)

        batch_len = 5
        for start in range(0, len(chunks), batch_len):
            batch = chunks[start : start + batch_len]
            userBatchContent = json.dumps(batch, ensure_ascii=False)
            messages: list[LLMMessageModel] = [
                LLMMessageModel(
                    role=LLmMessageRoleEnum.SYSTEM,
                    content=ExtractEntityGragSystemPrompt,
                ),
                LLMMessageModel(
                    role=LLmMessageRoleEnum.USER,
                    content=userBatchContent,
                ),
            ]
            LLMResponse = await llmService.Chat(
                modelParams=LLMRequestModel(
                    apiKey=GetCerebrasApiKey(),
                    model="qwen-3-235b-a22b-thinking-2507",
                    maxCompletionTokens=30000,
                    messages=messages,
                    temperature=0.4,
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
                                                items={
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            ),
                                            "relations": LLMResponseFormatPropertySchemaModel(
                                                type="array",
                                                items={
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                            ),
                                            "relationshipsEntities": LLMResponseFormatPropertySchemaModel(
                                                type="array",
                                                items={
                                                    "type": "array",
                                                    "items": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                    },
                                                },
                                            ),
                                            "chunks": LLMResponseFormatPropertySchemaModel(
                                                type="array", items={"type": "string"}
                                            ),
                                        },
                                        required=[
                                            "entities",
                                            "relations",
                                            "chunks",
                                            "relationshipsEntities",
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
