from pydantic import BaseModel


class RerankingRequestModel(BaseModel):
    model: str = "Salesforce/Llama-Rank-v1"
    query: str
    docs: list[str]
    topN: int = 5
