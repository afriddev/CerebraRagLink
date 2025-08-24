from together import AsyncTogether
from clientservices.embedding.models import RerankingRequestModel
from clientservices.embedding.implementations import RerankingImpl

rerankerClient = AsyncTogether(
    api_key="e01e224345314f2b1e73f6cf1503313223886531b13ff1829547f1bfe43c7690"
)


class RerankingService(RerankingImpl):

    async def FindRankingScore(self, modelParams: RerankingRequestModel):
        print(modelParams)

        response = await rerankerClient.rerank.create(
            model=modelParams.model,
            query=modelParams.query,
            documents=modelParams.docs,
            top_n=modelParams.topN,
        )
        print(response)
