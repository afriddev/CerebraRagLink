from typing import Any
from clientservices.embedding.models import (
    RerankingRequestModel,
    RerankingResponseModel,
    RerankingResponseChoiseModel,
    RerankingUsageModel,
    FindTopKresultsFromVectorsRequestModel,
    FindTopKresultsFromVectorsResponseModel,
)
import requests

from clientservices.chat.enums import ChatServiceResponseStatusEnum
from clientservices.embedding.implementations import RerankingImpl
from clientservices.embedding.workers import GetJinaApiKey
import numpy as np
import faiss


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

            if (
                response.get("model") is not None
                and response.get("results") is not None
            ):
                return RerankingResponseModel(
                    response=[
                        RerankingResponseChoiseModel(
                            index=choice.get("index"),
                            score=choice.get("relevance_score"),
                        )
                        for choice in response.get("results")
                    ],
                    usage=RerankingUsageModel(
                        totalTokens=response.get("usage").get("total_tokens")
                    ),
                    status=ChatServiceResponseStatusEnum.SUCCESS,
                )

            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.ERROR,
            )

        except Exception:
            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.SERVER_ERROR
            )

    def FindTopKResultsFromVectors(
        self, request: FindTopKresultsFromVectorsRequestModel
    ):
        try:
            sourceVec = np.array(request.sourceVectors, dtype="float32")
            queryVec = np.array([request.queryVector], dtype="float32")
            dim = sourceVec.shape[1]
            faissIndex: Any = faiss.IndexFlatL2(dim)
            faissIndex.add(sourceVec)
            distance, indeces = faissIndex.search(queryVec, request.topK)
            return FindTopKresultsFromVectorsResponseModel(
                distances=distance[0], indeces=indeces[0]
            )

        except Exception as e:
            print(e)
            return FindTopKresultsFromVectorsResponseModel(distances=None, indeces=None)
