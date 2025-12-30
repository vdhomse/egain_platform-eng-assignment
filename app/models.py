from pydantic import BaseModel, Field
from typing import List

class DocumentIngestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list, max_length=50)

class DocumentIngestResponse(BaseModel):
    document_id: str

class SearchResultItem(BaseModel):
    document_id: str
    title: str
    snippet: str
    relevance_score: float

class SearchResponse(BaseModel):
    query: str
    limit: int
    offset: int
    total: int
    results: List[SearchResultItem]
