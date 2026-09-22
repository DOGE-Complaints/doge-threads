"""t03 — L-OR-RDY /ready ready on live tables; degraded documented via stub."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from core.api.dependencies import ApiDependencies
from core.api.handlers import handle_readiness
from core.config import load_config_from_env
from core.infrastructure.providers import provide_service_factory
from tc05_live_fixtures import skip_unless_live_secrets
from tc06_traceability import TC06_SCENARIO_IDS


@pytest.mark.live_integration
def test_l_or_rdy_ready_when_tables_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    assert "L-OR-RDY-ready-when-tables-ok" in TC06_SCENARIO_IDS
    url, role = skip_unless_live_secrets()
    monkeypatch.setenv("APP_PROFILE", "demo")
    monkeypatch.setenv("DB_BACKEND", "supabase")
    monkeypatch.setenv("SUPABASE_URL", url)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE", role)
    from core.api.asgi_app import _clear_api_dependencies_cache, app

    _clear_api_dependencies_cache()
    client = TestClient(app)
    payload = client.get("/ready").json()
    assert payload["data"]["status"] == "ready"
    assert payload["data"]["db"]["backend"] == "supabase"
    assert payload["data"]["db"]["ready"] is True


def test_l_or_rdy_degraded_documented_via_stub() -> None:
    """Live cannot drop tables; stub documents degraded when probe/credentials fail."""
    assert "L-OR-RDY-degraded-documented" in TC06_SCENARIO_IDS
    config = load_config_from_env(
        {
            "APP_PROFILE": "demo",
            "DB_BACKEND": "supabase",
            "SUPABASE_URL": "",
            "SUPABASE_SERVICE_ROLE": "",
        }
    )
    factory = provide_service_factory(config)
    assert factory.db_ready is False
    assert factory.db_checks.get("credentials") is False
    deps = ApiDependencies(
        config=factory.config,
        db_backend=factory.db_backend,
        db_ready=factory.db_ready,
        db_checks=dict(factory.db_checks),
    )
    payload = handle_readiness(deps, trace_id="tc06-degraded")
    assert payload["data"]["status"] == "degraded"
    assert payload["data"]["db"]["ready"] is False
