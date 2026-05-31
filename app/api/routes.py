from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

from app.agent.graph import create_rag_agent, run_agent
from app.config import settings
from app.ingest.pipeline import IngestionPipeline
from app.models import HealthResponse, QueryRequest, QueryResponse, Source
from app.vectorstore.store import VectorStore

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    db_ok = False
    docs_count = 0
    try:
        vs = VectorStore()
        vs.initialize()
        docs_count = vs.count_documents()
        db_ok = True
    except Exception as e:
        logger.error("Health check DB failed: {e}", e=e)

    llm_ok = bool(settings.openrouter_api_key)

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        db=db_ok,
        llm=llm_ok,
        documents_count=docs_count,
    )


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = run_agent(request.question)
    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

    sources = [
        Source(**s) for s in result.get("sources", [])
    ]

    return QueryResponse(
        question=request.question,
        answer=result.get("answer", "No answer generated."),
        sources=sources,
        iterations=result.get("iterations", 1),
    )


@router.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    supported = {".pdf", ".md", ".txt"}
    ext = Path(file.filename or "").suffix.lower()

    if ext not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(supported)}",
        )

    documents_dir = settings.documents_dir
    documents_dir.mkdir(exist_ok=True)

    file_path = documents_dir / (file.filename or f"upload{ext}")

    try:
        content = await file.read()
        file_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}") from e

    try:
        pipeline = IngestionPipeline()
        vs = VectorStore()
        vs.initialize()
        chunk_count = pipeline.ingest_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest file: {e}") from e

    return {
        "filename": file.filename,
        "chunks_indexed": chunk_count,
        "status": "ok",
    }
