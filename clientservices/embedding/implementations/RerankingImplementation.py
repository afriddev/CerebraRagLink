from abc import ABC, abstractmethod
from clientservices.embedding.models import (
    RerankingRequestModel,
    RerankingResponseModel,
)


class RerankingImpl(ABC):

    @abstractmethod
    async def FindRankingScore(
        self, modelParams: RerankingRequestModel
    ) -> RerankingResponseModel:
        pass
