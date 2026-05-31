from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):  # type: ignore[misc]
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    database_url: str = "postgresql://kemi:kemi@localhost:5432/kemi"

    llm_model: str = "openai/gpt-4o-mini"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 2048

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    max_iterations: int = 3
    retrieval_top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 64

    api_host: str = "0.0.0.0"  # nosec - dev server binding
    api_port: int = 8000

    @property
    def documents_dir(self) -> Path:
        return Path("documents")


settings = Settings()
