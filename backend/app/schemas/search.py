"""Search API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    id: UUID
    result_type: str
    title: str
    excerpt: str | None = None
    slug: str | None = None
    score: float
    service_id: UUID | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int
    processing_ms: int


class SearchParams(BaseModel):
    q: str = Field(..., min_length=1, max_length=500)
    language: str = Field(default="auto")
    limit: int = Field(default=20, ge=1, le=100)
