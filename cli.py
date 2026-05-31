from __future__ import annotations

from pathlib import Path

import fire
from loguru import logger

from app.agent.graph import create_rag_agent, run_agent
from app.ingest.pipeline import IngestionPipeline
from app.logging import setup_logging
from app.vectorstore.store import VectorStore


def ingest(dir: str = "documents") -> None:
    """Indexer les documents d'un repertoire."""
    setup_logging()
    directory = Path(dir)
    if not directory.exists():
        logger.error("Directory not found: {dir}", dir=dir)
        return

    vs = VectorStore()
    vs.initialize()

    pipeline = IngestionPipeline(vector_store=vs)
    total = pipeline.ingest_directory(directory)
    logger.info("Ingestion terminee: {total} chunks indexes", total=total)


def query(q: str) -> None:
    """Poser une question a l'agent RAG."""
    setup_logging()

    vs = VectorStore()
    vs.initialize()

    result = run_agent(q)
    answer = result.get("answer", "No answer generated.")
    sources = result.get("sources", [])

    print(f"\nQuestion: {q}")
    print(f"Reponse: {answer}\n")

    if sources:
        print(f"Sources ({len(sources)}):")
        for s in sources:
            print(f"  - {s['document']} (score: {s['score']:.2f})")

    iterations = result.get("iterations", 1)
    print(f"\nIterations: {iterations}")


def stats() -> None:
    """Afficher les statistiques du vector store."""
    setup_logging()
    vs = VectorStore()
    vs.initialize()

    docs = vs.count_documents()
    chunks = vs.count_chunks()
    print(f"Documents: {docs}")
    print(f"Total chunks: {chunks}")


def serve() -> None:
    """Lancer le serveur FastAPI."""
    import uvicorn
    from app.config import settings
    setup_logging()
    uvicorn.run(
        "app.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )


def main() -> None:
    fire.Fire({
        "ingest": ingest,
        "query": query,
        "stats": stats,
        "serve": serve,
    })


if __name__ == "__main__":
    main()
