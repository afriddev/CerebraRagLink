from fastapi import APIRouter
from server.psqldb import PsqlDb
from server.services import QaRagControllerServices
from server.models import QaRagAskRequestModel


QaRag = APIRouter()
QaRaServices = QaRagControllerServices()


async def getDb() -> PsqlDb:
    from main import psqlDb

    return psqlDb


@QaRag.get("/rag/extarct")
async def HandleQaRag():
    response = await QaRaServices.QaRagExtarct(await getDb())
    return response


@QaRag.post("/rag/ask")
async def HandleQaRagAsk(request: QaRagAskRequestModel):
    response = await QaRaServices.QaRagAsk(
        request.query,
        await getDb(),
    )
    return response
