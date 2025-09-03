import aiohttp
import asyncio
import json
from sentence_transformers import CrossEncoder
import torch
import os

EVAL_FILE = "eval_data.json"     # your 500+ Q&A test set
RESULT_FILE = "eval_results.json"   # constant filename
ENDPOINT = "http://127.0.0.1:8001/api/v1/ask/chat/public"

# Load cross-encoder model
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")

async def fetch_answer(session, query):
    async with session.post(ENDPOINT, json={"id": None, "query": query}) as resp:
        answer = ""
        async for line in resp.content:
            line = line.decode("utf-8").strip()
            if line.startswith("data:"):
                answer += line.replace("data:", "").strip() + " "
        return answer.strip()

async def evaluate():
    with open(EVAL_FILE, "r") as f:
        eval_data = json.load(f)

    # Load existing results if file already exists (resume support)
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "r") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []
    else:
        results = []

    # Track completed IDs so we don’t redo them if restarting
    completed_ids = {r["id"] for r in results}

    async with aiohttp.ClientSession() as session:
        for idx, item in enumerate(eval_data, start=1):
            if idx in completed_ids:
                continue  # skip already done

            q = item["question"]
            expected = item["expected"]

            # Get RAG model answer
            answer = await fetch_answer(session, q)

            # Cross-encoder similarity
            score = model.predict([(expected, answer)])[0]
            similarity = torch.sigmoid(torch.tensor(score)).item()

            result = {
                "id": idx,
                "question": q,
                "expected": expected,
                "answer": answer,
                "similarity": round(similarity, 4)
            }
            results.append(result)

            # Write to file after each new result
            with open(RESULT_FILE, "w") as f:
                json.dump(results, f, indent=2)

            print(f"[{idx}/{len(eval_data)}] Score: {similarity:.2f} -> saved ✅")

    print(f"\n✅ Evaluation completed. Results saved to {RESULT_FILE}")

if __name__ == "__main__":
    asyncio.run(evaluate())
