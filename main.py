import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from dbservices import PsqlDb
from aiservices import RerankingService
from server import GragDocRouter,ChatRouter
from aiservices import ChatService

load_dotenv()

DATABASE_CONNECTION_STRING = os.getenv("DATABASE_CONNECTION_STRING", "")
psqlDb = PsqlDb(DATABASE_CONNECTION_STRING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await psqlDb.connect()
    yield
    # await psqlDb.close()


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
RerankingService()

ChatLLmService = ChatService()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:server", host="0.0.0.0", port=8001, reload=False)
