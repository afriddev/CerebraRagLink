from abc import ABC, abstractmethod
from aiservices.embedding.models import (
    RerankingRequestModel,
    RerankingResponseModel,
    FindTopKresultsFromVectorsRequestModel,
    FindTopKresultsFromVectorsResponseModel
)


class RerankingImpl(ABC):

    @abstractmethod
    async def FindRankingScore(
        self, modelParams: RerankingRequestModel
    ) -> RerankingResponseModel:
        pass

    @abstractmethod
    def FindTopKResultsFromVectors(self,request:FindTopKresultsFromVectorsRequestModel) -> FindTopKresultsFromVectorsResponseModel:
        pass
