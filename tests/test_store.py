from __future__ import annotations

import contextlib
from unittest.mock import MagicMock, patch

from app.vectorstore.store import VectorStore


class TestVectorStore:
    def test_init_default_connection_string(self) -> None:
        store = VectorStore()
        assert store.connection_string == "postgresql://test:test@localhost:5432/test"

    def test_init_custom_connection_string(self) -> None:
        store = VectorStore(connection_string="postgresql://user:pass@host:5432/db")
        assert store.connection_string == "postgresql://user:pass@host:5432/db"

    def test_engine_property(self) -> None:
        with patch("app.vectorstore.store.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine

            store = VectorStore()
            engine = store.engine

            assert engine == mock_engine
            mock_create.assert_called_once()

    def test_engine_property_cached(self) -> None:
        with patch("app.vectorstore.store.create_engine") as mock_create:
            store = VectorStore()
            engine1 = store.engine
            engine2 = store.engine

            assert engine1 is engine2
            mock_create.assert_called_once()

    def test_session_factory_property(self) -> None:
        with patch("app.vectorstore.store.create_engine"):
            mock_session_factory = MagicMock()
            with patch(
                "app.vectorstore.store.sessionmaker",
                return_value=mock_session_factory,
            ):
                store = VectorStore()
                factory = store.session_factory

                assert factory == mock_session_factory

    def test_document_exists_returns_true(self) -> None:
        mock_session = MagicMock()
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = MagicMock()

        store = VectorStore()
        with patch.object(store, "get_session") as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = mock_session

            result = store.document_exists("abc123")

            assert result is True

    def test_document_exists_returns_false(self) -> None:
        mock_session = MagicMock()
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None

        store = VectorStore()
        with patch.object(store, "get_session") as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = mock_session

            result = store.document_exists("abc123")

            assert result is False

    def test_count_documents(self) -> None:
        mock_session = MagicMock()
        mock_query = mock_session.query.return_value
        mock_distinct = mock_query.distinct.return_value
        mock_distinct.count.return_value = 5

        store = VectorStore()
        with patch.object(store, "get_session") as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = mock_session

            result = store.count_documents()

            assert result == 5

    def test_count_chunks(self) -> None:
        mock_session = MagicMock()
        mock_query = mock_session.query.return_value
        mock_query.count.return_value = 42

        store = VectorStore()
        with patch.object(store, "get_session") as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = mock_session

            result = store.count_chunks()

            assert result == 42

    def test_similarity_search(self) -> None:
        mock_session = MagicMock()
        mock_query = mock_session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.limit.return_value.all.return_value = [
            ("content1", "doc1.md", 0.1, 0),
            ("content2", "doc2.md", 0.2, 1),
        ]

        store = VectorStore()
        with patch.object(store, "get_session") as mock_ctx:
            mock_ctx.return_value.__enter__.return_value = mock_session

            results = store.similarity_search([0.1, 0.2, 0.3], top_k=2)

            assert len(results) == 2
            assert results[0] == ("content1", "doc1.md", 0.9, 0)
            assert results[1] == ("content2", "doc2.md", 0.8, 1)

    def test_insert_chunks_empty(self) -> None:
        store = VectorStore()
        with patch.object(store, "get_session") as mock_ctx:
            mock_session = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_session

            store.insert_chunks([], [])

            mock_session.add.assert_not_called()

    def test_get_session_commit_and_close(self) -> None:
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)

        store = VectorStore()
        store._session_factory = mock_factory

        with store.get_session() as session:
            assert session == mock_session

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_get_session_rollback_on_error(self) -> None:
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)

        store = VectorStore()
        store._session_factory = mock_factory

        with patch.object(store, "get_session") as mock_ctx:
            mock_ctx.return_value.__enter__.side_effect = ValueError("db error")

            with contextlib.suppress(ValueError):
                store.count_documents()

    def test_initialize(self) -> None:
        with (
            patch("app.vectorstore.store.Base.metadata.create_all") as mock_create,
            patch("app.vectorstore.store.create_engine") as mock_create_engine,
        ):
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            mock_conn = mock_engine.connect.return_value.__enter__.return_value

            store = VectorStore()
            store.initialize()

            mock_conn.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
            mock_create.assert_called_once_with(mock_engine)
