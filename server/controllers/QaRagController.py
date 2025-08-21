from fastapi import APIRouter
from server.psqldb import PsqlDb
from server.services import QaRagControllerServices
from server.models import QaRagAskRequestModel
from pydantic import BaseModel
from clientservices import EmbeddingService
import numpy as np

embeddingService = EmbeddingService()

class QaTestModel(BaseModel):
    answer:str
    question:str



QaRag = APIRouter()
QaRaServices = QaRagControllerServices()


async def getDb() -> PsqlDb:
    from main import psqlDb

    return psqlDb


@QaRag.get("/rag/extarct")
async def HandleQaRag():
    response = await QaRaServices.QaRagExtract(await getDb())
    return response


@QaRag.post("/rag/ask")
async def HandleQaRagAsk(request: QaRagAskRequestModel):
    response = await QaRaServices.QaRagAsk(
        request.query,
        await getDb(),
    )
    return response


@QaRag.post("/rag/test")
async def HandleRagTest(request: QaTestModel):
    # Get embeddings for both strings
    response = await embeddingService.ConvertTextToEmbedding([request.answer, request.question])
    
    a = np.array(response.data[0].embedding)
    b = np.array(response.data[1].embedding)
    
    # Cosine similarity
    cos_sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    # Euclidean distance
    euclidean_dist = float(np.linalg.norm(a - b))
    
    # Dot product
    dot_product = float(np.dot(a, b))
    
    return {
        "cosine_similarity": cos_sim,
        "euclidean_distance": euclidean_dist,
        "dot_product": dot_product
    }