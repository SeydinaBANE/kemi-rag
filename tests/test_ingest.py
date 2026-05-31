from __future__ import annotations

from pathlib import Path

from app.domain.schemas import Chunk, DocumentMetadata
from app.ingest.chunker import chunk_document
from app.ingest.loader import load_document


class TestLoader:
    def test_load_markdown(self, sample_markdown: Path) -> None:
        content = load_document(sample_markdown)
        assert "# Test Document" in content
        assert "Lorem ipsum" in content

    def test_load_text(self, sample_text: Path) -> None:
        content = load_document(sample_text)
        assert "This is a test text file." in content

    def test_unsupported_format(self, tmp_path: Path) -> None:
        path = tmp_path / "test.xyz"
        path.write_text("test")
        try:
            load_document(path)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestChunker:
    def test_chunk_basic(self) -> None:
        metadata = DocumentMetadata(
            filename="test.md",
            sha256="abc123",
            file_size=100,
        )
        content = "This is a test document. " * 50
        chunks = chunk_document(content, metadata)

        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.metadata.filename == "test.md" for c in chunks)

    def test_chunk_indices(self) -> None:
        metadata = DocumentMetadata(
            filename="test.md",
            sha256="abc123",
            file_size=100,
        )
        content = "Word " * 200
        chunks = chunk_document(content, metadata)

        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_chunk_content_preserved(self) -> None:
        metadata = DocumentMetadata(
            filename="test.md",
            sha256="abc123",
            file_size=50,
        )
        content = "Hello World"
        chunks = chunk_document(content, metadata)

        total = "".join(c.content for c in chunks)
        assert "Hello World" in total
