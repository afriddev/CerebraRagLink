from typing import Any
from dotenv import load_dotenv
import asyncpg
from pgvector.asyncpg import register_vector

load_dotenv()


class PsqlDb:
    def __init__(self, db_url: str):
        self.db_url: str = db_url
        self.pool: Any = None

    async def connect(self) -> None:
        async def _init(conn):
            # enable the extension if not already
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            # register pgvector type with asyncpg
            await register_vector(conn)

        self.pool = await asyncpg.create_pool(
            dsn=self.db_url,
            statement_cache_size=0,
            init=_init
        )

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