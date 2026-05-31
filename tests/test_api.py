from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.server import app

client = TestClient(app)


class TestHealth:
    def test_health_endpoint(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "db" in data
        assert "llm" in data

    def test_health_db_reachable(self) -> None:
        with patch("app.api.routes.VectorStore") as mock_vs_class:
            mock_store = mock_vs_class.return_value
            mock_store.count_documents.return_value = 10

            response = client.get("/health")
            data = response.json()

            assert data["status"] == "ok"
            assert data["db"] is True
            assert data["documents_count"] == 10

    def test_health_db_unreachable(self) -> None:
        with patch("app.api.routes.VectorStore") as mock_vs_class:
            mock_store = mock_vs_class.return_value
            mock_store.initialize.side_effect = ValueError("DB connection failed")

            response = client.get("/health")
            data = response.json()

            assert data["status"] == "degraded"
            assert data["db"] is False
            assert data["documents_count"] == 0

    def test_health_llm_key_missing(self) -> None:
        with patch("app.api.routes.settings.openrouter_api_key", ""):
            response = client.get("/health")
            data = response.json()

            assert data["llm"] is False

    def test_health_llm_key_present(self) -> None:
        with patch("app.api.routes.settings.openrouter_api_key", "sk-test-key"):
            response = client.get("/health")
            data = response.json()

            assert data["llm"] is True


class TestQuery:
    def test_query_empty_question(self) -> None:
        response = client.post("/query", json={"question": ""})
        assert response.status_code == 422

    def test_query_missing_question(self) -> None:
        response = client.post("/query", json={})
        assert response.status_code == 422

    def test_query_success(self) -> None:
        with patch("app.api.routes.run_agent") as mock_run:
            mock_run.return_value = {
                "question": "What is Python?",
                "answer": "Python is a programming language.",
                "sources": [
                    {
                        "document": "doc.md",
                        "content": "Python is...",
                        "score": 0.95,
                        "chunk_index": 0,
                    }
                ],
                "iterations": 2,
            }

            response = client.post("/query", json={"question": "What is Python?"})

            assert response.status_code == 200
            data = response.json()
            assert data["question"] == "What is Python?"
            assert data["answer"] == "Python is a programming language."
            assert len(data["sources"]) == 1
            assert data["iterations"] == 2

    def test_query_no_sources(self) -> None:
        with patch("app.api.routes.run_agent") as mock_run:
            mock_run.return_value = {
                "question": "test",
                "answer": "Answer.",
                "sources": [],
                "iterations": 1,
            }

            response = client.post("/query", json={"question": "test"})
            assert response.status_code == 200
            assert response.json()["sources"] == []

    def test_query_no_answer_in_result(self) -> None:
        with patch("app.api.routes.run_agent") as mock_run:
            mock_run.return_value = {
                "question": "test",
                "sources": [],
                "iterations": 1,
            }

            response = client.post("/query", json={"question": "test"})
            assert response.status_code == 200
            assert response.json()["answer"] == "No answer generated."

    def test_query_agent_error(self) -> None:
        with patch("app.api.routes.run_agent") as mock_run:
            mock_run.side_effect = ValueError("Agent crashed")

            response = client.post("/query", json={"question": "What is Python?"})

            assert response.status_code == 500
            assert "Agent crashed" in response.json()["detail"]


class TestIngest:
    def test_ingest_unsupported_format(self) -> None:
        response = client.post(
            "/ingest",
            files={"file": ("test.exe", b"fake content", "application/x-msdownload")},
        )
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]

    def test_ingest_markdown_success(self) -> None:
        with patch("app.api.routes.IngestionPipeline") as mock_pipeline_cls:
            mock_pipeline = mock_pipeline_cls.return_value
            mock_pipeline.ingest_file.return_value = 3

            with patch("app.api.routes.VectorStore"):
                response = client.post(
                    "/ingest",
                    files={"file": ("test.md", b"# Hello", "text/markdown")},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["filename"] == "test.md"
                assert data["chunks_indexed"] == 3
                assert data["status"] == "ok"

    def test_ingest_file_save_error(self) -> None:
        with patch("app.api.routes.Path.write_bytes") as mock_write:
            mock_write.side_effect = PermissionError("Permission denied")

            response = client.post(
                "/ingest",
                files={"file": ("test.md", b"# Hello", "text/markdown")},
            )

            assert response.status_code == 500
            assert "Failed to save file" in response.json()["detail"]

    def test_ingest_pipeline_error(self) -> None:
        with patch("app.api.routes.IngestionPipeline") as mock_pipeline_cls:
            mock_pipeline = mock_pipeline_cls.return_value
            mock_pipeline.ingest_file.side_effect = ValueError("Ingestion failed")

            with patch("app.api.routes.VectorStore"):
                response = client.post(
                    "/ingest",
                    files={"file": ("test.md", b"# Hello", "text/markdown")},
                )

                assert response.status_code == 500
                assert "Failed to ingest file" in response.json()["detail"]
