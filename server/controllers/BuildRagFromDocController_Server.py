from fastapi import APIRouter
from server.services import BuildRagService

GragDocRouter = APIRouter()
BuildRag = BuildRagService()


@GragDocRouter.get("/brfd")
async def BuildRagFromDoc():
    return await BuildRag.BuildRag("./others/a.xlsx")
