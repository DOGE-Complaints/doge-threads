"""t04 — STORY-THREADS-TC-08 story gate: E-HTTP TRACEABILITY + AC-THR-01."""

from __future__ import annotations

from pathlib import Path

from core.api.asgi_app import app
from tc08_traceability import TC08_SCENARIO_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_TC08_FILES = (
    _TESTS / "tc08_traceability.py",
    _TESTS / "test_tc08_health.py",
    _TESTS / "test_tc08_ready_matrix.py",
    _TESTS / "test_tc08_route_set.py",
    _TESTS / "test_story_gate_tc_08.py",
)


def test_all_e_http_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC08_FILES)
    missing = sorted(item for item in TC08_SCENARIO_IDS if item not in corpus)
    assert missing == []
    families = set()
    for item in TC08_SCENARIO_IDS:
        if item.startswith("E-HTTP-HLTH-"):
            families.add("HLTH")
        elif item.startswith("E-HTTP-RDY-"):
            families.add("RDY")
        elif item.startswith("E-HTTP-AC01-"):
            families.add("AC01")
    assert families == {"HLTH", "RDY", "AC01"}


def test_ac_thr_01_no_new_public_routes() -> None:
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == ["/health", "/ready"]
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    assert '@app.post("/thread' not in asgi
