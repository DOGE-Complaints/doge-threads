"""t01 — H-MK markers + make targets."""

from __future__ import annotations

from pathlib import Path

from tc09_traceability import TC09_SCENARIO_IDS

_ROOT = Path(__file__).resolve().parents[1]
_PYPROJECT = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
_MAKEFILE = (_ROOT / "Makefile").read_text(encoding="utf-8")
_GH = (_ROOT / ".github" / "workflows" / "test-offline.yml").read_text(encoding="utf-8")


def test_h_mk_markers_registered() -> None:
    assert "H-MK-live-integration" in TC09_SCENARIO_IDS
    assert "H-MK-domain-e2e" in TC09_SCENARIO_IDS
    assert "live_integration" in _PYPROJECT
    assert "domain_e2e" in _PYPROJECT


def test_h_mk_make_targets() -> None:
    assert "H-MK-test" in TC09_SCENARIO_IDS
    assert "H-MK-test-live" in TC09_SCENARIO_IDS
    assert "H-MK-test-e2e-domain" in TC09_SCENARIO_IDS
    assert "\ntest:\n" in _MAKEFILE or _MAKEFILE.startswith("test:") or "\ntest:" in _MAKEFILE
    assert "test-live:" in _MAKEFILE
    assert "test-e2e-domain:" in _MAKEFILE
    assert 'not live_integration and not domain_e2e' in _MAKEFILE


def test_h_mk_gh_offline_unchanged() -> None:
    assert "not live_integration" in _GH
    assert "test-live" not in _GH
    assert "live_integration:" not in _GH
