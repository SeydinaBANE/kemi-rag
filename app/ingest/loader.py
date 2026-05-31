from __future__ import annotations

from pathlib import Path

from loguru import logger


def load_document(path: Path) -> str:
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _load_pdf(path)
    elif ext == ".md" or ext == ".txt":
        return _load_text(path)
    else:
        msg = f"Unsupported file type: {ext}"
        raise ValueError(msg)


def _load_pdf(path: Path) -> str:
    try:
        import fitz
    except ImportError:
        msg = "PyMuPDF (fitz) is required for PDF loading. Install with: pip install pymupdf"
        raise ImportError(msg) from None

    text_parts: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(page_text)

    content = "\n\n".join(text_parts)
    logger.info(
        "Loaded PDF: {path} ({pages} pages, {chars} chars)",
        path=path.name,
        pages=len(doc),
        chars=len(content),
    )
    return content


def _load_text(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    logger.info("Loaded text file: {path} ({chars} chars)", path=path.name, chars=len(content))
    return content
