from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from loguru import logger
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Float, Integer, String, Text, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import settings
from app.domain.schemas import Chunk

Base = declarative_base()


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_name = Column(String(512), nullable=False)
    document_hash = Column(String(64), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)


class VectorStore:
    def __init__(self, connection_string: str | None = None) -> None:
        self.connection_string = connection_string or settings.database_url
        self._engine = None
        self._session_factory = None

    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                echo=False,
            )
        return self._engine

    @property
    def session_factory(self):
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def initialize(self) -> None:
        with self.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(self.engine)
        logger.info("Vector store initialized")

    def document_exists(self, document_hash: str) -> bool:
        with self.get_session() as session:
            return (
                session.query(DocumentChunk)
                .filter(DocumentChunk.document_hash == document_hash)
                .first()
                is not None
            )

    def insert_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return

        with self.get_session() as session:
            for chunk, embedding in zip(chunks, embeddings):
                db_chunk = DocumentChunk(
                    document_name=chunk.metadata.filename,
                    document_hash=chunk.metadata.sha256,
                    chunk_index=chunk.index,
                    content=chunk.content,
                    embedding=embedding,
                )
                session.add(db_chunk)

    def similarity_search(self, embedding: list[float], top_k: int = 5) -> list[tuple[str, str, float, int]]:
        with self.get_session() as session:
            results = (
                session.query(
                    DocumentChunk.content,
                    DocumentChunk.document_name,
                    DocumentChunk.embedding.cosine_distance(embedding).label("distance"),
                    DocumentChunk.chunk_index,
                )
                .filter(DocumentChunk.embedding.isnot(None))
                .order_by("distance")
                .limit(top_k)
                .all()
            )

        return [
            (content, doc_name, float(1.0 - dist), chunk_idx)
            for content, doc_name, dist, chunk_idx in results
        ]

    def count_documents(self) -> int:
        with self.get_session() as session:
            return session.query(DocumentChunk.document_hash).distinct().count()

    def count_chunks(self) -> int:
        with self.get_session() as session:
            return session.query(DocumentChunk).count()
