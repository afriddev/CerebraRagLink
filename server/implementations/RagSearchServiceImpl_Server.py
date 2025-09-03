from abc import ABC, abstractmethod
from server.models import SearchOnDbResponseModel


class RagSearchServiceImpl_Server(ABC):

    @abstractmethod
    async def SearchOnDb_Server(self, query: str) -> SearchOnDbResponseModel:
        pass
