from mistralai import Mistral, models, EmbeddingResponse
from clientservices.mistral.models import (
    EmbeddingResponseModel,
    EmbeddingDataModel,
    EmbeddingUsageModel,
)
from clientservices.mistral.enums import EmbeddingResponseEnum
from clientservices.mistral.workers import GetMistralApiKey


mistralClient = Mistral(api_key=GetMistralApiKey())


class EmbeddingService:
    async def ConvertTextToEmbedding(self, text: list[str]) -> EmbeddingResponseModel:
        try:
            res: EmbeddingResponse = await mistralClient.embeddings.create_async(
                model="mistral-embed",
                inputs=text,
            )

            data = [
                EmbeddingDataModel(
                    embedding=obj.embedding,
                    index=obj.index,
                )
                for obj in res.data
            ]
            usage = EmbeddingUsageModel(
                completionTokens=res.usage.completion_tokens,
                promptTokens=res.usage.prompt_tokens,
                totalTokens=res.usage.total_tokens,
            )

            return EmbeddingResponseModel(
                data=data,
                usage=usage,
                id=res.id,
                status=EmbeddingResponseEnum.SUCCESS,
            )

        except models.HTTPValidationError:
            return EmbeddingResponseModel(status=EmbeddingResponseEnum.VALIDATION_ERROR)
        except models.SDKError:
            return EmbeddingResponseModel(status=EmbeddingResponseEnum.SERVER_ERROR)
