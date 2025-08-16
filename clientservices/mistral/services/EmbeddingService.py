from clientservices.mistral.implementations import EmbeddingServiceImpl
from mistralai import EmbeddingResponse, Mistral, models
from clientservices.mistral.models import (
    EmbeddingResponseModel,
    EmbeddingDataModel,
    EmbeddingUsageModel,
)
from clientservices.mistral.enums import EmbeddingResponseEnum
from clientservices.mistral.workers import GetMistralApiKey


class EmbeddingService(EmbeddingServiceImpl):
    async def ConvertTextToEmbedding(self, text: list[str]) -> EmbeddingResponseModel:
        async with Mistral(
            api_key=GetMistralApiKey(),
        ) as mistral:
            try:
                res: EmbeddingResponse = await mistral.embeddings.create_async(
                    model="mistral-embed",
                    inputs=text,
                )
                data: list[EmbeddingDataModel] = []
                for dataObjet in res.data:
                    data.append(
                        EmbeddingDataModel(
                            embedding=dataObjet.embedding,
                            index=dataObjet.index,
                        )
                    )
                usage: EmbeddingUsageModel = EmbeddingUsageModel(
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
            except models.HTTPValidationError as e:
                print(e)

                return EmbeddingResponseModel(
                    status=EmbeddingResponseEnum.VALIDATION_ERROR
                )
            except models.SDKError as e:
                return EmbeddingResponseModel(status=EmbeddingResponseEnum.SERVER_ERROR)
