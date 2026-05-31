from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from app.embeddings.provider import EmbeddingProvider, get_embedding_provider


class TestEmbeddingProvider:
    def test_embed_caches_result(self) -> None:
        provider = EmbeddingProvider(model_name="test-model")

        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])

        with patch.object(provider, "_model", mock_model):
            result1 = provider.embed("hello")
            result2 = provider.embed("hello")

            assert result1 == result2
            mock_model.encode.assert_called_once()

    def test_embed_different_texts(self) -> None:
        provider = EmbeddingProvider(model_name="test-model")

        mock_model = MagicMock()

        def encode_side_effect(text: str, **kwargs: object) -> np.ndarray:
            mapping = {"foo": np.array([0.1, 0.2]), "bar": np.array([0.3, 0.4])}
            return mapping[text]

        mock_model.encode.side_effect = encode_side_effect

        with patch.object(provider, "_model", mock_model):
            r1 = provider.embed("foo")
            r2 = provider.embed("bar")
            r3 = provider.embed("foo")

            assert r3 == r1
            assert r2 != r1

    def test_embed_model_loaded_on_demand(self) -> None:
        with patch("app.embeddings.provider.SentenceTransformer") as mock_transformer:
            mock_instance = MagicMock()
            mock_instance.encode.return_value = np.array([0.1, 0.2])
            mock_transformer.return_value = mock_instance

            provider = EmbeddingProvider(model_name="test-model")
            assert provider._model is None

            result = provider.embed("hello")

            mock_transformer.assert_called_once_with("test-model")
            assert result == [0.1, 0.2]

    def test_embed_batch_all_uncached(self) -> None:
        provider = EmbeddingProvider(model_name="test-model")

        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])

        with patch.object(provider, "_model", mock_model):
            results = provider.embed_batch(["a", "b", "c"])

            assert len(results) == 3
            mock_model.encode.assert_called_once()

    def test_embed_batch_mixed_cache(self) -> None:
        provider = EmbeddingProvider(model_name="test-model")

        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.3, 0.4]])

        with patch.object(provider, "_model", mock_model):
            provider._cache["a"] = [0.1, 0.2]
            results = provider.embed_batch(["a", "b"])

            assert len(results) == 2
            assert results[0] == [0.1, 0.2]
            assert results[1] == [0.3, 0.4]
            mock_model.encode.assert_called_once()

    def test_embed_batch_all_cached(self) -> None:
        provider = EmbeddingProvider(model_name="test-model")

        mock_model = MagicMock()

        with patch.object(provider, "_model", mock_model):
            provider._cache["a"] = [0.1, 0.2]
            provider._cache["b"] = [0.3, 0.4]

            results = provider.embed_batch(["a", "b"])

            assert len(results) == 2
            mock_model.encode.assert_not_called()

    def test_dimension(self) -> None:
        provider = EmbeddingProvider(model_name="test-model")

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 768

        with patch.object(provider, "_model", mock_model):
            assert provider.dimension == 768

    def test_dimension_none(self) -> None:
        provider = EmbeddingProvider(model_name="test-model")

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = None

        with patch.object(provider, "_model", mock_model):
            assert provider.dimension == 384

    def test_get_embedding_provider_singleton(self) -> None:
        with patch("app.embeddings.provider.SentenceTransformer"):
            p1 = get_embedding_provider()
            p2 = get_embedding_provider()

            assert p1 is p2
