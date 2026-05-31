from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.domain.schemas import Chunk, DocumentMetadata


def chunk_document(content: str, metadata: DocumentMetadata) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len,
    )

    texts = splitter.split_text(content)
    chunks = [Chunk(content=text, index=i, metadata=metadata) for i, text in enumerate(texts)]

    return chunks
