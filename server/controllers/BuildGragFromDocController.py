from fastapi import APIRouter


GragDocRouter = APIRouter()


@GragDocRouter.get("/health")
async def health_check():
    return {"status": "ok"}
