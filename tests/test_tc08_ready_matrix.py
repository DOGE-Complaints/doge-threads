"""t02 — E-HTTP-RDY /ready backend matrix."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from core.api.asgi_app import _clear_api_dependencies_cache, app
from core.infrastructure.db_supabase import SupabaseDatabase
from tc05_live_fixtures import skip_unless_live_secrets
from tc08_traceability import TC08_SCENARIO_IDS


def _client(monkeypatch: pytest.MonkeyPatch, **env: str) -> TestClient:
    monkeypatch.setenv("APP_PROFILE", "demo")
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    _clear_api_dependencies_cache()
    return TestClient(app)


def test_e_http_rdy_in_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "E-HTTP-RDY-in-memory" in TC08_SCENARIO_IDS
    client = _client(monkeypatch, DB_BACKEND="in_memory")
    payload = client.get("/ready").json()["data"]
    assert client.get("/ready").status_code == 200
    assert payload["status"] == "ready"
    assert payload["db"]["backend"] == "in_memory"
    assert payload["db"]["ready"] is True


def test_e_http_rdy_supabase_missing_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "E-HTTP-RDY-supabase-missing-creds" in TC08_SCENARIO_IDS
    client = _client(
        monkeypatch,
        DB_BACKEND="supabase",
        SUPABASE_URL="",
        SUPABASE_SERVICE_ROLE="",
    )
    payload = client.get("/ready").json()["data"]
    assert payload["status"] == "degraded"
    assert payload["db"]["backend"] == "supabase"
    assert payload["db"]["ready"] is False
    assert payload["db"]["checks"].get("credentials") is False


def test_e_http_rdy_tables_missing_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "E-HTTP-RDY-tables-missing" in TC08_SCENARIO_IDS
    monkeypatch.setattr(SupabaseDatabase, "required_tables_ready", lambda self: False)
    client = _client(
        monkeypatch,
        DB_BACKEND="supabase",
        SUPABASE_URL="http://example.test",
        SUPABASE_SERVICE_ROLE="test-role",
    )
    payload = client.get("/ready").json()["data"]
    assert payload["status"] == "degraded"
    assert payload["db"]["ready"] is False
    assert payload["db"]["checks"].get("tables") is False


def test_e_http_rdy_tables_ok_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "E-HTTP-RDY-tables-ok" in TC08_SCENARIO_IDS
    monkeypatch.setattr(SupabaseDatabase, "required_tables_ready", lambda self: True)
    client = _client(
        monkeypatch,
        DB_BACKEND="supabase",
        SUPABASE_URL="http://example.test",
        SUPABASE_SERVICE_ROLE="test-role",
    )
    payload = client.get("/ready").json()["data"]
    assert payload["status"] == "ready"
    assert payload["db"]["ready"] is True
    assert payload["db"]["checks"].get("tables") is True


@pytest.mark.live_integration
def test_e_http_rdy_tables_ok_live_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "E-HTTP-RDY-tables-ok" in TC08_SCENARIO_IDS
    url, role = skip_unless_live_secrets()
    client = _client(
        monkeypatch,
        DB_BACKEND="supabase",
        SUPABASE_URL=url,
        SUPABASE_SERVICE_ROLE=role,
    )
    payload = client.get("/ready").json()["data"]
    assert payload["status"] == "ready"
    assert payload["db"]["ready"] is True
