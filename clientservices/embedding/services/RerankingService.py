from together import AsyncTogether
from clientservices.embedding.models import (
    RerankingRequestModel,
    RerankingResponseModel,
    RerankingResponseChoiseModel,
)
from clientservices.embedding.implementations import RerankingImpl

rerankerClient = AsyncTogether(
    api_key="e01e224345314f2b1e73f6cf1503313223886531b13ff1829547f1bfe43c7690"
)


class RerankingService(RerankingImpl):

    async def FindRankingScore(
        self, modelParams: RerankingRequestModel
    ) -> RerankingResponseModel:

        response = await rerankerClient.rerank.create(
            model=modelParams.model,
            query=modelParams.query,
            documents=modelParams.docs,
            top_n=modelParams.topN,
        )
        response:list[RerankingResponseChoiseModel] = []
        for rankResponse in response.results:

        print(response)
