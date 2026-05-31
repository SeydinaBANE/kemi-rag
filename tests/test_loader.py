from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.ingest.loader import _load_pdf, _load_text, load_document


class TestLoadDocument:
    def test_load_document_markdown(self, sample_markdown: Path) -> None:
        content = load_document(sample_markdown)
        assert "# Test Document" in content
        assert "Lorem ipsum" in content

    def test_load_document_text(self, sample_text: Path) -> None:
        content = load_document(sample_text)
        assert "This is a test text file." in content

    def test_load_document_unsupported(self) -> None:
        with pytest.raises(ValueError, match="Unsupported file type"):
            load_document(Path("test.xyz"))

    def test_load_document_pdf(self, sample_pdf: Path) -> None:
        mock_page_1 = MagicMock()
        mock_page_1.get_text.return_value = "Page 1 content"
        mock_page_2 = MagicMock()
        mock_page_2.get_text.return_value = "  "

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2
        mock_doc.__iter__.return_value = iter([mock_page_1, mock_page_2])

        mock_fitz = MagicMock()
        mock_fitz.open.return_value.__enter__.return_value = mock_doc

        with patch.dict("sys.modules", {"fitz": mock_fitz}):
            content = load_document(sample_pdf)

        assert "Page 1 content" in content


class TestLoadPdf:
    def test_load_pdf_import_error(self) -> None:
        import builtins
        from typing import Any

        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> Any:
            if name == "fitz":
                raise ImportError
            return original_import(name, *args, **kwargs)

        with (
            patch("builtins.__import__", side_effect=mock_import),
            pytest.raises(ImportError, match="PyMuPDF"),
        ):
            _load_pdf(Path("test.pdf"))

    def test_load_pdf_empty_pages(self) -> None:
        mock_page = MagicMock()
        mock_page.get_text.return_value = ""

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__iter__.return_value = iter([mock_page])

        mock_fitz = MagicMock()
        mock_fitz.open.return_value.__enter__.return_value = mock_doc

        with patch.dict("sys.modules", {"fitz": mock_fitz}):
            content = _load_pdf(Path("test.pdf"))

        assert content == ""

    def test_load_pdf_multiple_pages(self) -> None:
        mock_page_1 = MagicMock()
        mock_page_1.get_text.return_value = "Page 1"
        mock_page_2 = MagicMock()
        mock_page_2.get_text.return_value = "Page 2"
        mock_page_3 = MagicMock()
        mock_page_3.get_text.return_value = ""

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3
        mock_doc.__iter__.return_value = iter([mock_page_1, mock_page_2, mock_page_3])

        mock_fitz = MagicMock()
        mock_fitz.open.return_value.__enter__.return_value = mock_doc

        with patch.dict("sys.modules", {"fitz": mock_fitz}):
            content = _load_pdf(Path("test.pdf"))

        assert "Page 1" in content
        assert "Page 2" in content


class TestLoadText:
    def test_load_text(self, sample_text: Path) -> None:
        content = _load_text(sample_text)
        assert content == "This is a test text file.\nIt has multiple lines.\nFor testing purposes."

    def test_load_text_unicode(self, tmp_path: Path) -> None:
        path = tmp_path / "unicode.txt"
        path.write_text("café résumé")
        content = _load_text(path)
        assert content == "café résumé"
