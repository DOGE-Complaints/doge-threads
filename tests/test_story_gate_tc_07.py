"""t04 — STORY-THREADS-TC-07 story gate: E-DOM TRACEABILITY + AC-THR-01."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from tc07_traceability import TC07_SCENARIO_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_MAKEFILE = _TESTS.parent / "Makefile"
_TC07_FILES = (
    _TESTS / "tc07_traceability.py",
    _TESTS / "tc07_e2e_fixtures.py",
    _TESTS / "test_tc07_env_contract.py",
    _TESTS / "test_tc07_happy.py",
    _TESTS / "test_tc07_deny.py",
    _TESTS / "test_story_gate_tc_07.py",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_all_e_dom_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC07_FILES)
    missing = sorted(item for item in TC07_SCENARIO_IDS if item not in corpus)
    assert missing == []
    families = set()
    for item in TC07_SCENARIO_IDS:
        if item.startswith("E-DOM-HAPPY-"):
            families.add("HAPPY")
        elif item.startswith("E-DOM-DENY-"):
            families.add("DENY")
    assert families == {"HAPPY", "DENY"}


def test_make_test_e2e_domain_target() -> None:
    makefile = _MAKEFILE.read_text(encoding="utf-8")
    assert "test-e2e-domain:" in makefile
    assert "-m domain_e2e" in makefile


def test_ac_thr_01_no_new_public_routes() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment"):
        assert f'@app.get("{name}' not in asgi
        assert f'@app.post("{name}' not in asgi
