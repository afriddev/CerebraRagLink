import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from dbservices import PsqlDb
from clientservices import RerankingService

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
RerankingService()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:server", host="192.168.167.117", port=8001, reload=False)
