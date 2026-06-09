from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from api import app


def test_status_returns_empty_on_startup():
    with patch("app.api.poll_urls", new_callable=AsyncMock):
        with TestClient(app) as client:
            response = client.get("/status")
            assert response.status_code == 200
            assert isinstance(response.json(), dict)


def test_status_returns_results():
    from data import add_result

    add_result("https://example.com", "2026-06-07T00:00:00Z", 42.0, "200")

    with patch("app.api.poll_urls", new_callable=AsyncMock):
        with TestClient(app) as client:
            response = client.get("/status")
            assert "https://example.com" in response.json()
