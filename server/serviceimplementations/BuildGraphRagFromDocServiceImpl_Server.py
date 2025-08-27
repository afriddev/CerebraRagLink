from abc import ABC, abstractmethod


class BuildGraphRagFromDocServiceImpl_Server(ABC):

    @abstractmethod
    async def BuildGraphFromDoc(self, file:str):
        pass
