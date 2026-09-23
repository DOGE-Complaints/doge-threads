"""t04 — STORY-THREADS-TC-06 story gate: L-OR TRACEABILITY + AC-THR-01."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from tc06_traceability import TC06_SCENARIO_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_TC06_FILES = (
    _TESTS / "tc06_traceability.py",
    _TESTS / "tc06_live_fixtures.py",
    _TESTS / "test_tc06_factory_live.py",
    _TESTS / "test_tc06_write_reread.py",
    _TESTS / "test_tc06_ready.py",
    _TESTS / "test_story_gate_tc_06.py",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_all_l_or_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC06_FILES)
    missing = sorted(item for item in TC06_SCENARIO_IDS if item not in corpus)
    assert missing == []
    families = set()
    for item in TC06_SCENARIO_IDS:
        if item.startswith("L-OR-WR-"):
            families.add("WR")
        elif item.startswith("L-OR-RR-"):
            families.add("RR")
        elif item.startswith("L-OR-RDY-"):
            families.add("RDY")
    assert families == {"WR", "RR", "RDY"}


def test_ac_thr_01_no_new_public_routes() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment"):
        assert f'@app.get("{name}' not in asgi
        assert f'@app.post("{name}' not in asgi
