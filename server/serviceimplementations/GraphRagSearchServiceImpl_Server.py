from abc import ABC, abstractmethod
from typing import Any


class GraphRagSearchServiceImpl_Server(ABC):

    @abstractmethod
    async def SearchOnDb_Server(self, query: str,db:Any):
        pass
