from typing import Any
from fastapi.responses import JSONResponse, StreamingResponse
from abc import ABC, abstractmethod


class QaRagContollerImpl(ABC):

    @abstractmethod
    async def QaRagExtract(self,db:Any) -> JSONResponse:
        pass
    
    @abstractmethod
    async def QaRagAsk(self,query:str,db:Any) -> StreamingResponse:
        pass

