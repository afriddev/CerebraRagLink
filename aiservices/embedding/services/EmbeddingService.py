from mistralai import Mistral, models, EmbeddingResponse
from aiservices.embedding.implementations import EmbeddingServiceImpl
from aiservices.embedding.models import (
    EmbeddingResponseModel,
    EmbeddingDataModel,
    EmbeddingUsageModel)
from aiservices.embedding.enums import EmbeddingResponseEnum
from aiservices.embedding.workers import GetMistralApiKey
import numpy as np


mistralClient = Mistral(api_key=GetMistralApiKey())

class EmbeddingService(EmbeddingServiceImpl):
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

        except models.HTTPValidationError as e:
            print(e)
            return EmbeddingResponseModel(status=EmbeddingResponseEnum.VALIDATION_ERROR)
        except models.SDKError as e:
            print(e)

            return EmbeddingResponseModel(status=EmbeddingResponseEnum.SERVER_ERROR)

    def FindSimilarity(self, vec1: list[float], vec2: list[float]) -> float:
        if len(vec1) != len(vec2):
            return 0.0
        else:
            a = np.array(vec1)
            b = np.array(vec2)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    
