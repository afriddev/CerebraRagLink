from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from aiservices import RerankingService, EmbeddingService
from server import GragDocRouter, ChatRouter
from aiservices import ChatService
import asyncio

from config.PsqlDbConfig import psqlDb

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(psqlDb.connect())
    yield
    try:
        await asyncio.wait_for(psqlDb.close(), timeout=3)
    except asyncio.TimeoutError:
        print("⚠️ DB close timed out")


server = FastAPI(lifespan=lifespan)

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
server.include_router(GragDocRouter, prefix="/api/v1")
server.include_router(ChatRouter, prefix="/api/v1/ask")
RerankingService = RerankingService()

ChatLLmService = ChatService()
EmbeddingService = EmbeddingService()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:server", host="0.0.0.0", port=8001, reload=False)
