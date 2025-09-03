from fastapi import FastAPI, Query
from sentence_transformers import CrossEncoder
import torch

MODELS = {
    "stsb-roberta-large": CrossEncoder("cross-encoder/stsb-roberta-large", num_labels=1),
    "nli-deberta-v3-base": CrossEncoder("cross-encoder/nli-deberta-v3-base", num_labels=3),
    "ms-marco-MiniLM-L-12-v2": CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-12-v2", num_labels=1, activation_fn=torch.nn.Sigmoid()
    ),
}

app = FastAPI()

def normalize_score(model_name, model, q1, q2):
    pair = [(q1, q2)]
    if "stsb" in model_name:
        score = model.predict(pair)[0]
        return float(score)
    elif "nli" in model_name:
        probs = model.predict(pair, apply_softmax=True)[0]
        return float(probs[1] + probs[2])
    else:
        score = model.predict(pair)[0]
        return float(score)

@app.get("/similarity")
def get_similarity(q1: str = Query(...), q2: str = Query(...)):
    results = {name: normalize_score(name, model, q1, q2) for name, model in MODELS.items()}
    return {"q1": q1, "q2": q2, "similarities": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test:app", host="0.0.0.0", port=8001, reload=True)
