import os
from rag.implementations import EmbeddingServiceImpl
from mistralai import EmbeddingResponse, Mistral, models
from rag.models import (
    ConvertTextToEmbeddingResponseErrorModel,
    ConvertTextToEmbeddingResponseDataModel,
    ConvertTextToEmbeddingResponseUsageModel,
)
from rag.enums import ConvertTextToEmbeddingResponseErrorEnums
from dotenv import load_dotenv

load_dotenv()


MISTRA_API_KEY = os.getenv("MISTRAL_API_KEY", "")


class EmbeddingService(EmbeddingServiceImpl):
    async def ConvertTextToEmbedding(
        self, text: list[str]
    ) -> ConvertTextToEmbeddingResponseErrorModel:
        async with Mistral(
            api_key=MISTRA_API_KEY,
        ) as mistral:
            try:
                res: EmbeddingResponse = await mistral.embeddings.create_async(
                    model="mistral-embed",
                    inputs=text,
                )
                data: list[ConvertTextToEmbeddingResponseDataModel] = []
                for dataObjet in res.data:
                    data.append(
                        ConvertTextToEmbeddingResponseDataModel(
                            embedding=dataObjet.embedding,
                            index=dataObjet.index,
                        )
                    )
                usage: ConvertTextToEmbeddingResponseUsageModel = (
                    ConvertTextToEmbeddingResponseUsageModel(
                        completionTokens=res.usage.completion_tokens,
                        promptTokens=res.usage.prompt_tokens,
                        totalTokens=res.usage.total_tokens,
                    )
                )
                return ConvertTextToEmbeddingResponseErrorModel(
                    data=data,
                    usage=usage,
                    id=res.id,
                    status=ConvertTextToEmbeddingResponseErrorEnums.SUCCESS,
                )
            except models.HTTPValidationError as e:
                print(e)

                return ConvertTextToEmbeddingResponseErrorModel(
                    status=ConvertTextToEmbeddingResponseErrorEnums.VALIDATION_ERROR
                )
            except models.SDKError as e:
                return ConvertTextToEmbeddingResponseErrorModel(
                    status=ConvertTextToEmbeddingResponseErrorEnums.SERVER_ERROR
                )
