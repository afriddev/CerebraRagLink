from typing import Any
from dotenv import load_dotenv
import asyncpg

load_dotenv()


class PsqlDb:
    def __init__(self, db_url: str):
        self.db_url: str = db_url
        self.pool:Any = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(self.db_url,statement_cache_size=0)

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()

    async def get_connection(self) -> asyncpg.Connection:
        if self.pool is None:
            raise RuntimeError("Connection pool is not initialized. Call connect() first.")
        return await self.pool.acquire()

    async def release_connection(self, conn: asyncpg.Connection) -> None:
        if self.pool is None:
            raise RuntimeError("Connection pool is not initialized. Call connect() first.")
        await self.pool.release(conn)


