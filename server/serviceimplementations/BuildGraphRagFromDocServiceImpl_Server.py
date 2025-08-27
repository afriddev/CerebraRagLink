from abc import ABC, abstractmethod
from typing import Any


class BuildGraphRagFromDocServiceImpl_Server(ABC):

    @abstractmethod
    async def BuildGraphFromDoc(self, file:str,db:Any):
        pass
