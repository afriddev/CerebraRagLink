from abc import ABC, abstractmethod
from clientservices.embedding.models import RerankingRequestModel


class RerankingImpl(ABC):

    @abstractmethod
    async def FindRankingScore(self, modelParams: RerankingRequestModel):
        pass
