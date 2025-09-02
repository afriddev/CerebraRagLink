from pydantic import BaseModel


class SearchOnDbImageModel_Server(BaseModel):
    url: str
    description: str


class SearchOnDbDocModel_Server(BaseModel):
    matchedText: str
    contextText: str
    images: list[SearchOnDbImageModel_Server]


class SearchOnDbResponseModel(BaseModel):
    docs: list[SearchOnDbDocModel_Server]
