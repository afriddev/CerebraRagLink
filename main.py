import asyncio
import time
import math
from infinity_emb import AsyncEngineArray, EngineArgs, AsyncEmbeddingEngine

# --- SETTINGS ---
MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
BATCH_SIZE = 32          # safe for 8GB RAM
EMBED_DIM_TYPE = "int4"  # fastest on CPU
MAX_LENGTH = 256         # adjust for your chunk size
TOTAL_ROWS = 20000       # number of chunks/texts

# Generate dummy data
chunks = [f"Sample text {i}" for i in range(TOTAL_ROWS)]

# Create async Infinity engine
array = AsyncEngineArray.from_args([
    EngineArgs(
        model_name_or_path=MODEL_ID,
        engine="torch",
        embedding_dtype=EMBED_DIM_TYPE,
        dtype="auto",
        max_length=MAX_LENGTH
    )
])

async def embed_all(engine: AsyncEmbeddingEngine):
    async with engine:
        embeddings = []
        start_time = time.time()
        total_batches = math.ceil(len(chunks) / BATCH_SIZE)

        for batch_idx in range(total_batches):
            batch = chunks[batch_idx * BATCH_SIZE : (batch_idx + 1) * BATCH_SIZE]
            vecs, usage = await engine.embed(sentences=batch)
            embeddings.extend(vecs)

            done = (batch_idx + 1) * BATCH_SIZE
            elapsed = time.time() - start_time
            speed = done / elapsed
            eta = (len(chunks) - done) / speed
            print(f"Batch {batch_idx+1}/{total_batches} - "
                  f"Processed: {done} | Speed: {speed:.1f} rows/s | ETA: {eta:.1f}s")

        print(f"\n✅ Finished {len(chunks)} rows in {time.time() - start_time:.1f} seconds.")
        print(f"Embedding size: {len(embeddings[0])}")

asyncio.run(embed_all(array[0]))
