from abc import ABC, abstractmethod
from typing import Any
from server.models import SearchOnDbResponseModel


class GraphRagSearchServiceImpl_Server(ABC):

    @abstractmethod
    async def SearchOnDb_Server(self, query: str, db: Any) -> SearchOnDbResponseModel:
        pass
