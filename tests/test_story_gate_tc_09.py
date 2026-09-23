"""t05 — STORY-THREADS-TC-09 story gate: H-* + AC-THR-01 + package Done."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from tc09_traceability import TC09_SCENARIO_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_TRACE = (
    _TESTS.parent
    / "docs"
    / "tasks"
    / "backlog-stories"
    / "req01-test-hardening"
    / "TRACEABILITY.md"
)
_TC09_FILES = (
    _TESTS / "tc09_traceability.py",
    _TESTS / "test_tc09_markers_makefile.py",
    _TESTS / "test_tc09_conftest.py",
    _TESTS / "test_tc09_traceability_md.py",
    _TESTS / "test_tc09_gap_map.py",
    _TESTS / "test_story_gate_tc_09.py",
)
_GH = (_TESTS.parent / ".github" / "workflows" / "test-offline.yml").read_text(encoding="utf-8")


def test_all_h_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC09_FILES)
    missing = sorted(item for item in TC09_SCENARIO_IDS if item not in corpus)
    assert missing == []
    families = set()
    for item in TC09_SCENARIO_IDS:
        families.add(item.split("-", 2)[1])
    assert families == {"MK", "CF", "TR", "GAP"}


def test_package_done_gate_artifacts() -> None:
    assert _TRACE.is_file()
    text = _TRACE.read_text(encoding="utf-8")
    assert "Package Done gate" in text
    assert "G5" in text
    assert "not live_integration" in _GH


def test_ac_thr_01_no_new_public_routes() -> None:
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == CURRENT_PUBLIC_GET_PATHS
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    assert '@app.put("/threads/issues/{issue_id}/reactions")' in asgi
    assert '@app.put("/threads/by-issue' not in asgi
    assert '@app.post("/threads/issues/{issue_id}/attachment-refs' not in asgi
