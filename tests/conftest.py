from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from app.config import Settings


@pytest.fixture(autouse=True)
def test_settings(monkeypatch: MonkeyPatch) -> Generator[Settings, None, None]:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")

    from app.config import settings

    settings.openrouter_api_key = "sk-test-key"
    settings.database_url = "postgresql://test:test@localhost:5432/test"

    yield settings


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"  # noqa: E501
    path = tmp_path / "test.pdf"
    path.write_bytes(content)
    return path


@pytest.fixture
def sample_markdown(tmp_path: Path) -> Path:
    content = """# Test Document

This is a test markdown document for unit testing.

## Section 1
Lorem ipsum dolor sit amet, consectetur adipiscing elit.

## Section 2
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
"""
    path = tmp_path / "test.md"
    path.write_text(content)
    return path


@pytest.fixture
def sample_text(tmp_path: Path) -> Path:
    content = "This is a test text file.\nIt has multiple lines.\nFor testing purposes."
    path = tmp_path / "test.txt"
    path.write_text(content)
    return path
