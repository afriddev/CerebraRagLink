from services import EmbeddingService
import asyncio
import time  # <- Import time module

async def main():
    service = EmbeddingService()
    text_to_embed = ["Embed this sentence."]
    
    start_time = time.perf_counter()  # Start the timer
    embeddings = await service.ConvertTextToEmbedding(text_to_embed)
    end_time = time.perf_counter()  # End the timer

    print("Embeddings received:", embeddings.data)
    print(f"Latency: {end_time - start_time:.4f} seconds")  # Print elapsed time

if __name__ == "__main__":
    asyncio.run(main())
