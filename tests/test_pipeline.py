from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.ingest.pipeline import IngestionPipeline


class TestIngestionPipeline:
    def test_ingest_file_success(self, sample_markdown: Path) -> None:
        mock_store = MagicMock()
        mock_store.document_exists.return_value = False
        mock_embedder = MagicMock()
        mock_embedder.embed_batch.return_value = [[0.1, 0.2]] * 3

        pipeline = IngestionPipeline(vector_store=mock_store, embedding_provider=mock_embedder)

        with (
            patch("app.ingest.pipeline.sha256_file", return_value="abc123"),
            patch("app.ingest.pipeline.chunk_document") as mock_chunk,
        ):
            mock_chunks = [
                MagicMock(content="chunk1", metadata=MagicMock()),
                MagicMock(content="chunk2", metadata=MagicMock()),
                MagicMock(content="chunk3", metadata=MagicMock()),
            ]
            mock_chunk.return_value = mock_chunks

            result = pipeline.ingest_file(sample_markdown)

            assert result == 3
            mock_store.document_exists.assert_called_once_with("abc123")
            mock_store.insert_chunks.assert_called_once()
            mock_embedder.embed_batch.assert_called_once_with(["chunk1", "chunk2", "chunk3"])

    def test_ingest_file_already_exists(self, sample_markdown: Path) -> None:
        mock_store = MagicMock()
        mock_store.document_exists.return_value = True
        mock_embedder = MagicMock()

        pipeline = IngestionPipeline(vector_store=mock_store, embedding_provider=mock_embedder)

        with patch("app.ingest.pipeline.sha256_file", return_value="abc123"):
            result = pipeline.ingest_file(sample_markdown)

            assert result == 0
            mock_store.insert_chunks.assert_not_called()

    def test_ingest_directory(self, tmp_path: Path) -> None:
        (tmp_path / "doc1.md").write_text("# Doc 1")
        (tmp_path / "doc2.txt").write_text("Doc 2")

        pipeline = IngestionPipeline(vector_store=MagicMock(), embedding_provider=MagicMock())

        with patch.object(pipeline, "ingest_file", return_value=3) as mock_ingest:
            result = pipeline.ingest_directory(tmp_path)

            assert result == 6
            assert mock_ingest.call_count == 2

    def test_ingest_directory_no_files(self, tmp_path: Path) -> None:
        (tmp_path / "readme.xyz").write_text("unsupported")

        pipeline = IngestionPipeline(vector_store=MagicMock(), embedding_provider=MagicMock())

        with patch.object(pipeline, "ingest_file") as mock_ingest:
            result = pipeline.ingest_directory(tmp_path)

            assert result == 0
            mock_ingest.assert_not_called()

    def test_ingest_directory_partial_failure(self, tmp_path: Path) -> None:
        (tmp_path / "good.md").write_text("# Good")
        (tmp_path / "bad.md").write_text("# Bad")

        pipeline = IngestionPipeline(vector_store=MagicMock(), embedding_provider=MagicMock())

        with patch.object(pipeline, "ingest_file") as mock_ingest:
            mock_ingest.side_effect = [5, ValueError("fail")]

            result = pipeline.ingest_directory(tmp_path)

            assert result == 5
            assert mock_ingest.call_count == 2

    def test_ingest_directory_skips_unsupported_ext(self, tmp_path: Path) -> None:
        (tmp_path / "doc.md").write_text("# Doc")
        (tmp_path / "image.png").write_bytes(b"fake png")

        pipeline = IngestionPipeline(vector_store=MagicMock(), embedding_provider=MagicMock())

        with patch.object(pipeline, "ingest_file", return_value=2) as mock_ingest:
            result = pipeline.ingest_directory(tmp_path)

            assert result == 2
            mock_ingest.assert_called_once()

    def test_ingest_file_tracks_metadata(self, sample_markdown: Path) -> None:
        mock_store = MagicMock()
        mock_store.document_exists.return_value = False
        mock_embedder = MagicMock()
        mock_embedder.embed_batch.return_value = [[0.1, 0.2]]

        pipeline = IngestionPipeline(vector_store=mock_store, embedding_provider=mock_embedder)

        with (
            patch("app.ingest.pipeline.sha256_file", return_value="def456"),
            patch("app.ingest.pipeline.chunk_document") as mock_chunk,
        ):
            mock_chunk.return_value = [MagicMock(content="chunk1", metadata=MagicMock())]

            pipeline.ingest_file(sample_markdown)

            call_chunks = mock_store.insert_chunks.call_args[0][0]
            assert len(call_chunks) == 1
