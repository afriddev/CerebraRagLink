from fastapi import APIRouter
from fastapi.responses import JSONResponse
from server.psqldb import PsqlDb
from rag import TextChunkService

QaRag = APIRouter()


async def getDb() -> PsqlDb:
    from main import psqlDb

    return psqlDb


@QaRag.get("/rag/extarct")
async def handleQaRag():
    textChunkService = TextChunkService()
    result = await textChunkService.HandleQuestionAndAnswersProcessForRag("a.pdf")

    return JSONResponse(
        status_code=result.status.value[0], content={"data": result.status.value[1]}
    )
