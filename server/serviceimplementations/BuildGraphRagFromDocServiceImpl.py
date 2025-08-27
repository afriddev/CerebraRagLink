from abc import ABC, abstractmethod


class BuildGraphRagFromDocServiceImpl(ABC):

    @abstractmethod
    async def BuildGraphFromDoc(self, file:str):
        pass
