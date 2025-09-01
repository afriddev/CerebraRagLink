from fastapi import APIRouter
from server.services import BuildRagFromDocService_Server

GragDocRouter = APIRouter()
BuildRagFromDocServiceServer = BuildRagFromDocService_Server()


@GragDocRouter.get("/brfd")
async def BuildRagFromDoc():
    return await BuildRagFromDocServiceServer.BuildRagFromDoc("./others/a.csv")
