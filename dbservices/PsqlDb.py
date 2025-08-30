from typing import Any
from dotenv import load_dotenv
import asyncpg
import asyncio
from pgvector.asyncpg import register_vector

load_dotenv()


class PsqlDb:
    def __init__(self, db_url: str):
        self.db_url: str = db_url
        self.pool: Any = None

    async def connect(self) -> None:
        async def _init(conn):
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await register_vector(conn)

        retries = 3
        for i in range(retries):
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=self.db_url,
                    min_size=1,
                    max_size=10,
                    statement_cache_size=0,
                    init=_init
                )
                return
            except Exception as e:
                print(f"[DB] Connection failed: {e} (retry {i+1}/{retries})")
                await asyncio.sleep(2)
        raise RuntimeError("Failed to connect to PostgreSQL after retries")

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()

    async def get_connection(self):
        if self.pool is None:
            raise RuntimeError("Connection pool is not initialized. Call connect() first.")
        return self.pool
