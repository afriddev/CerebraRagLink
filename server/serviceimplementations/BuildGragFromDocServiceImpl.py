from abc import ABC, abstractmethod


class BuildGragFromDocServiceImpl(ABC):

    @abstractmethod
    async def BuildGraphFromDoc(self, doc_path: str, doc_type: str):
        pass
