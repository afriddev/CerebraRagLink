from clientservices.mistral.enums.ChatEnums import MistralChatMessageRoleEnum
from clientservices.mistral.models.ChatModels import MistralChatRequestMessageModel
from graphrag.implementations import FileChunkGragImpl
from utils import ExtractTextFromDoc
from langchain.text_splitter import RecursiveCharacterTextSplitter
from clientservices import MistralChatService,MistralChatRequestModel
from graphrag.models import LLMGragEntityResponseModel
from graphrag.utils.GragSystemPropts import ExtractEntityGragSystemPrompt


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
        chunks = self.ExatrctChunkFromText(file, 500)

        batchIndex: int = 0
        batchLength: int = 5

        while batchIndex   * batchLength < len(chunks):
            batch = chunks[batchIndex : batchIndex + batchLength]
            
            chatRequest =  MistralChatRequestModel(
                model="mistral-small-2506",
                messages=[
                    MistralChatRequestMessageModel(
                        role=MistralChatMessageRoleEnum.SYSTEM,
                        content=ExtractEntityGragSystemPrompt,   # ✅ system rules
                    ),
                    MistralChatRequestMessageModel(
                        role=MistralChatMessageRoleEnum.USER,
                        content=batch,   # ✅ your array of chunks
                    )
                    ],
                responseFormat=LLMGragEntityResponseModel,
                temperature=0.7,
                maxTokens=1000,
                stream=False,
            )
            chatResponse = await mistralService.Chat(modelParams=chatRequest)
            print(chatResponse.choices[0].message.content)
            
            batchIndex += 1
