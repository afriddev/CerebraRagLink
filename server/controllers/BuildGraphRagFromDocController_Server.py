from fastapi import APIRouter
from dbservices import PsqlDb
from server.services import BuildGraphRagFromDocService_Server

GragDocRouter = APIRouter()
BuildGraphRagFromDocServiceServer = BuildGraphRagFromDocService_Server()


async def GetDb() -> PsqlDb:
    from main import psqlDb

    return psqlDb


@GragDocRouter.get("/bgrfd")
async def BuildGraphFromDoc():
    return await BuildGraphRagFromDocServiceServer.BuildGraphFromDoc(
        "./others/a.xlsx", await GetDb()
    )

