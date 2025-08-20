from typing import Any, cast
from clientservices.mistral.enums.ChatEnums import MistralChatMessageRoleEnum
from clientservices.mistral.models.ChatModels import MistralChatRequestMessageModel
from graphrag.implementations import FileChunkGragImpl
from utils import ExtractTextFromDoc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from clientservices import MistralChatService, MistralChatRequestModel
from graphrag.models import LLMGragEntityResponseModel
from graphrag.utils.GragSystemPropts import ExtractEntityGragSystemPrompt
import json


mistralService = MistralChatService()


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
        chunks = self.ExatrctChunkFromText(file, 1000,100)

        batch_len = 5
        for start in range(0, len(chunks), batch_len):
            batch = chunks[start : start + batch_len]

            user_payload = json.dumps(batch, ensure_ascii=False)

            chatRequest = MistralChatRequestModel(
                model="mistral-small-2506",
                messages=[
                    MistralChatRequestMessageModel(
                        role=MistralChatMessageRoleEnum.SYSTEM,
                        content=ExtractEntityGragSystemPrompt,  # use the prompt above
                    ),
                    MistralChatRequestMessageModel(
                        role=MistralChatMessageRoleEnum.USER,
                        content=user_payload,  # <-- JSON array of chunk strings
                    ),
                ],
                responseFormat=LLMGragEntityResponseModel,  # matches the model above
                temperature=0.0,
                maxTokens=4000,
                stream=False,
            )

            chatResponse = await mistralService.Chat(modelParams=chatRequest)
            print(json.loads(chatResponse.choices[0].message.content))
