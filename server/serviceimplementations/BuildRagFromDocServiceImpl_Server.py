from abc import ABC, abstractmethod


class BuildRagFromDocServiceImpl_Server(ABC):

    @abstractmethod
    async def BuildGraphRagFromDoc(self, file:str):
        pass
    
    @abstractmethod
    async def BuildRagFromDoc(self, file:str):
        pass

