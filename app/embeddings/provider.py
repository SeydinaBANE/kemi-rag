from __future__ import annotations

from functools import lru_cache

import numpy as np
from cachetools import LRUCache  # type: ignore[import-untyped]
from loguru import logger
from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingProvider:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.embedding_model
        self._model: SentenceTransformer | None = None
        self._cache: LRUCache[str, list[float]] = LRUCache(maxsize=10000)

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading embedding model: {model}", model=self.model_name)
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, text: str) -> list[float]:
        if text in self._cache:
            return self._cache[text]  # type: ignore[no-any-return]
        embedding: list[float] = self.model.encode(text, normalize_embeddings=True).tolist()
        self._cache[text] = embedding
        return embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        uncached: list[tuple[int, str]] = []
        results: list[list[float] | None] = [None] * len(texts)

        for i, text in enumerate(texts):
            cached = self._cache.get(text)
            if cached is not None:
                results[i] = cached
            else:
                uncached.append((i, text))

        if uncached:
            indices, texts_to_embed = zip(*uncached, strict=False)
            embeddings = self.model.encode(
                list(texts_to_embed),
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            for idx, emb in zip(indices, embeddings, strict=False):
                emb_list: list[float] = emb.tolist() if isinstance(emb, np.ndarray) else emb
                self._cache[texts[idx]] = emb_list
                results[idx] = emb_list

        return [r for r in results if r is not None]

    @property
    def dimension(self) -> int:
        result = self.model.get_sentence_embedding_dimension()
        return int(result)


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    return EmbeddingProvider()
