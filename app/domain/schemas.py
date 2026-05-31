from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    filename: str
    sha256: str
    page_count: int | None = None
    file_size: int = 0


class Chunk(BaseModel):
    content: str
    index: int
    metadata: DocumentMetadata


class GradingResult(BaseModel):
    binary_score: str = Field(..., pattern=r"^(yes|no)$")
    reasoning: str = ""


class RetrievalResult(BaseModel):
    content: str
    score: float
    document: str
    chunk_index: int


class AgentIteration(BaseModel):
    iteration: int
    action: str
    result: str = ""
