from typing import Any
from clientservices.embedding.models import (
    RerankingRequestModel,
    RerankingResponseModel,
    RerankingResponseChoiseModel,
    RerankingUsageModel,
)
import requests

from clientservices.chat.enums import ChatServiceResponseStatusEnum
from clientservices.embedding.implementations import RerankingImpl
from clientservices.embedding.workers import GetJinaApiKey

jinaClient = requests.Session()
jinaClient.headers.update(
    {
        "Authorization": f"Bearer {GetJinaApiKey()}",
        "Content-Type": "application/json",
    }
)


class RerankingService(RerankingImpl):

    async def FindRankingScore(
        self, modelParams: RerankingRequestModel
    ) -> RerankingResponseModel:
        try:

            data: Any = {
                "model": modelParams.model,
                "query": modelParams.query,
                "documents": modelParams.docs,
                "top_n": modelParams.topN,
                "return_documents": modelParams.returnDocuments,
            }
            res = jinaClient.post("https://api.jina.ai/v1/rerank", json=data)
            response = res.json()
            
            if response.get("model") is not None and response.get("results") is not None:
                return RerankingResponseModel(
                    response=[
                        RerankingResponseChoiseModel(
                            index=choice.get("index"), score=choice.get("relevance_score")
                        )
                        for choice in response.get("results")
                    ],
                    usage=RerankingUsageModel(totalTokens=response.get("usage").get("total_tokens")),
                    status=ChatServiceResponseStatusEnum.SUCCESS,
                )

            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.ERROR,
            )

        except Exception:
            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.SERVER_ERROR
            )
