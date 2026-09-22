"""t01 — E-HTTP-HLTH /health 200 always."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from core.api.asgi_app import _clear_api_dependencies_cache, app
from tc08_traceability import TC08_SCENARIO_IDS


def _client(monkeypatch: pytest.MonkeyPatch, **env: str) -> TestClient:
    monkeypatch.setenv("APP_PROFILE", "demo")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    _clear_api_dependencies_cache()
    return TestClient(app)


@pytest.mark.parametrize(
    "backend_env",
    (
        {"DB_BACKEND": "in_memory"},
        {
            "DB_BACKEND": "supabase",
            "SUPABASE_URL": "",
            "SUPABASE_SERVICE_ROLE": "",
        },
    ),
)
def test_e_http_hlth_always_200(
    monkeypatch: pytest.MonkeyPatch, backend_env: dict[str, str]
) -> None:
    assert "E-HTTP-HLTH-always-200" in TC08_SCENARIO_IDS
    client = _client(monkeypatch, **backend_env)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"
