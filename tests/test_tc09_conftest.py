"""t02 — H-CF conftest live opt-in."""

from __future__ import annotations

from pathlib import Path

from tc09_traceability import TC09_SCENARIO_IDS

_CONFTEST = (Path(__file__).resolve().parent / "conftest.py").read_text(encoding="utf-8")


def test_h_cf_default_in_memory() -> None:
    assert "H-CF-default-in-memory" in TC09_SCENARIO_IDS
    assert 'monkeypatch.setenv("DB_BACKEND", "in_memory")' in _CONFTEST
    assert 'monkeypatch.setenv("SUPABASE_URL", "")' in _CONFTEST
    assert 'monkeypatch.setenv("SUPABASE_SERVICE_ROLE", "")' in _CONFTEST


def test_h_cf_live_keep_supabase() -> None:
    assert "H-CF-live-keep-supabase" in TC09_SCENARIO_IDS
    assert 'get_closest_marker("live_integration")' in _CONFTEST
    assert '"domain_e2e"' in _CONFTEST
    assert "return" in _CONFTEST
