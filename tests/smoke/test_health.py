from __future__ import annotations

from fastapi.testclient import TestClient

from core.api.asgi_app import app


def test_health_public(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_ready_ok(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["status"] in {"ready", "degraded"}
    assert payload["db"]["backend"] == "in_memory"


def test_smoke_asgi_paths_health_ready_only() -> None:
    paths = sorted(
        {
            getattr(route, "path", None)
            for route in app.routes
            if getattr(route, "methods", None)
        }
    )
    assert paths == ["/health", "/ready"]
