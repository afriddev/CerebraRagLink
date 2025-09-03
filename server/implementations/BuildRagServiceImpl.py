from abc import ABC, abstractmethod


class BuildRagServiceImpl(ABC):

    @abstractmethod
    async def BuildRag(self, file:str):
        pass
    
