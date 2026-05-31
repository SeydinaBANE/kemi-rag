from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="La question a poser")
    top_k: int | None = Field(None, ge=1, le=20, description="Nombre de documents a retrouver")


class Source(BaseModel):
    document: str = Field(..., description="Nom du document source")
    chunk_index: int = Field(..., ge=0)
    content: str = Field(..., description="Extrait pertinent")
    score: float = Field(..., ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source] = Field(default_factory=list)
    iterations: int = Field(default=1, ge=1)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class HealthResponse(BaseModel):
    status: str
    db: bool = False
    llm: bool = False
    documents_count: int = 0
