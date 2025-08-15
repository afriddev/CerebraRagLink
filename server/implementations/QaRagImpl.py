from typing import Any
from fastapi.responses import JSONResponse
from abc import ABC, abstractmethod


class QaRagContollerImpl(ABC):

    @abstractmethod
    async def QaRagExtarct(self,db:Any) -> JSONResponse:
        pass
    
    @abstractmethod
    async def QaRagAsk(self,query:str,db:Any) -> JSONResponse:
        pass

