from typing import Any
from together import AsyncTogether
import together.error as APIError
from clientservices.embedding.models import (
    RerankingRequestModel,
    RerankingResponseModel,
    RerankingResponseChoiseModel,
    RerankingUsageModel,
)

from clientservices.chat.enums import ChatServiceResponseStatusEnum

from clientservices.embedding.implementations import RerankingImpl

rerankerClient = AsyncTogether(
    api_key="e01e224345314f2b1e73f6cf1503313223886531b13ff1829547f1bfe43c7690"
)


class RerankingService(RerankingImpl):

    async def FindRankingScore(
        self, modelParams: RerankingRequestModel
    ) -> RerankingResponseModel:

        try:
            response: Any = await rerankerClient.rerank.create(
                model=modelParams.model,
                query=modelParams.query,
                documents=modelParams.docs,
                top_n=modelParams.topN,
            )
            if response.id is not None and response.results is not None:
                return RerankingResponseModel(
                    response=[
                        RerankingResponseChoiseModel(
                            index=choice.index, score=choice.relevance_score
                        )
                        for choice in response.results
                    ],
                    usage=RerankingUsageModel(totalTokens=response.usage.total_tokens),
                    status=ChatServiceResponseStatusEnum.SUCCESS,
                )

            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.ERROR,
            )

        except APIError.InvalidRequestError:
            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.BAD_REQUEST
            )
        except APIError.AuthenticationError:
            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.UNAUTHROZIED
            )
        except APIError.RequestException:
            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.BAD_REQUEST
            )

        except Exception as e:
            print(e)
            return RerankingResponseModel(
                status=ChatServiceResponseStatusEnum.SERVER_ERROR
            )
