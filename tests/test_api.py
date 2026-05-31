from __future__ import annotations

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


class TestQuery:
    def test_query_empty_question(self) -> None:
        response = client.post("/query", json={"question": ""})
        assert response.status_code == 422

    def test_query_missing_question(self) -> None:
        response = client.post("/query", json={})
        assert response.status_code == 422


class TestIngest:
    def test_ingest_unsupported_format(self) -> None:
        response = client.post(
            "/ingest",
            files={"file": ("test.exe", b"fake content", "application/x-msdownload")},
        )
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]
