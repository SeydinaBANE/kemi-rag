from __future__ import annotations

from pathlib import Path

from loguru import logger

from app.domain.schemas import Chunk, DocumentMetadata
from app.embeddings.provider import EmbeddingProvider
from app.ingest.chunker import chunk_document
from app.ingest.loader import load_document
from app.utils.hash import sha256_file
from app.vectorstore.store import VectorStore


class IngestionPipeline:
    def __init__(
        self,
        vector_store: VectorStore | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.vector_store = vector_store or VectorStore()
        self.embedding_provider = embedding_provider or EmbeddingProvider()

    def ingest_file(self, path: Path) -> int:
        file_hash = sha256_file(str(path))

        if self.vector_store.document_exists(file_hash):
            logger.info("Skipping already indexed document: {path} (hash: {hash})", path=path.name, hash=file_hash[:12])
            return 0

        content = load_document(path)
        metadata = DocumentMetadata(
            filename=path.name,
            sha256=file_hash,
            file_size=path.stat().st_size,
        )
        chunks = chunk_document(content, metadata)

        texts = [c.content for c in chunks]
        embeddings = self.embedding_provider.embed_batch(texts)

        self.vector_store.insert_chunks(chunks, embeddings)
        logger.info(
            "Indexed {path}: {count} chunks, hash={hash}",
            path=path.name,
            count=len(chunks),
            hash=file_hash[:12],
        )
        return len(chunks)

    def ingest_directory(self, directory: Path) -> int:
        extensions = {".pdf", ".md", ".txt"}
        files = [f for f in directory.rglob("*") if f.suffix.lower() in extensions]
        total = 0

        if not files:
            logger.warning("No supported documents found in {dir}", dir=directory)
            return 0

        logger.info("Found {count} documents to process", count=len(files))
        for file in sorted(files):
            try:
                total += self.ingest_file(file)
            except Exception:
                logger.exception("Failed to ingest {path}", path=file)

        logger.info("Ingestion complete: {total} chunks indexed", total=total)
        return total
