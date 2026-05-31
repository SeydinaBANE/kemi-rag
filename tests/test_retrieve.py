from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.agent.nodes.retrieve import retrieve_node
from app.agent.state import GraphState


def _make_state(
    question: str,
    rewritten_question: str = "",
) -> GraphState:
    return {
        "question": question,
        "rewritten_question": rewritten_question,
        "context": [],
        "documents": [],
        "sources": [],
        "answer": "",
        "iterations": 0,
        "messages": [],
        "trace": [],
    }


class TestRetrieveNode:
    def test_retrieve_node_uses_original_question(self) -> None:
        state = _make_state("What is Python?")

        mock_store = MagicMock()
        mock_store.similarity_search.return_value = []

        mock_embedder = MagicMock()
        mock_embedder.embed.return_value = [0.1, 0.2, 0.3]

        result = retrieve_node(state, vector_store=mock_store, embedding_provider=mock_embedder)

        mock_embedder.embed.assert_called_once_with("What is Python?")
        assert result["context"] == []
        assert result["sources"] == []
        assert result["documents"] == []

    def test_retrieve_node_uses_rewritten_question(self) -> None:
        state = _make_state("What is it?", rewritten_question="What is Python?")

        mock_store = MagicMock()
        mock_store.similarity_search.return_value = []

        mock_embedder = MagicMock()
        mock_embedder.embed.return_value = [0.1, 0.2, 0.3]

        retrieve_node(state, vector_store=mock_store, embedding_provider=mock_embedder)

        mock_embedder.embed.assert_called_once_with("What is Python?")

    def test_retrieve_node_with_results(self) -> None:
        state = _make_state("What is Python?")

        mock_store = MagicMock()
        mock_store.similarity_search.return_value = [
            ("Python is a language.", "doc.md", 0.95, 0),
            ("Python is interpreted.", "doc.md", 0.90, 1),
        ]

        mock_embedder = MagicMock()
        mock_embedder.embed.return_value = [0.1, 0.2, 0.3]

        result = retrieve_node(state, vector_store=mock_store, embedding_provider=mock_embedder)

        assert result["context"] == ["Python is a language.", "Python is interpreted."]
        assert result["documents"] == ["doc.md", "doc.md"]
        assert len(result["sources"]) == 2
        assert result["sources"][0]["document"] == "doc.md"
        assert result["sources"][0]["score"] == 0.95

    def test_retrieve_node_default_instances(self) -> None:
        state = _make_state("What is Python?")

        with (
            patch("app.agent.nodes.retrieve.VectorStore") as mock_vs_cls,
            patch("app.agent.nodes.retrieve.EmbeddingProvider") as mock_ep_cls,
        ):
            mock_store = MagicMock()
            mock_store.similarity_search.return_value = []
            mock_vs_cls.return_value = mock_store

            mock_embedder = MagicMock()
            mock_embedder.embed.return_value = [0.1, 0.2, 0.3]
            mock_ep_cls.return_value = mock_embedder

            retrieve_node(state)

            mock_vs_cls.assert_called_once()
            mock_ep_cls.assert_called_once()
