"""t06 — STORY-THREADS-TC-05 story gate: L-PG TRACEABILITY + env-gate + AC-THR-01."""

from __future__ import annotations

from pathlib import Path

from core.api.asgi_app import app
from tc05_traceability import TC05_SCENARIO_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_MAKEFILE = _TESTS.parent / "Makefile"
_TC05_FILES = (
    _TESTS / "tc05_traceability.py",
    _TESTS / "tc05_live_fixtures.py",
    _TESTS / "test_tc05_env_gate.py",
    _TESTS / "test_tc05_readiness_schema.py",
    _TESTS / "test_tc05_roundtrip.py",
    _TESTS / "test_tc05_unique_rls.py",
    _TESTS / "test_tc05_cleanup.py",
    _TESTS / "test_story_gate_tc_05.py",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_all_l_pg_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC05_FILES)
    missing = sorted(item for item in TC05_SCENARIO_IDS if item not in corpus)
    assert missing == []
    families = set()
    for item in TC05_SCENARIO_IDS:
        if item.startswith("L-PG-RDY-"):
            families.add("RDY")
        elif item.startswith("L-PG-SCH-"):
            families.add("SCH")
        elif item.startswith("L-PG-RT-"):
            families.add("RT")
        elif item.startswith("L-PG-UQ-"):
            families.add("UQ")
        elif item.startswith("L-PG-RLS-"):
            families.add("RLS")
        elif item.startswith("L-PG-CLN-"):
            families.add("CLN")
    assert families == {"RDY", "SCH", "RT", "UQ", "RLS", "CLN"}


def test_no_unconditional_live_skip() -> None:
    stub = (_TESTS / "test_providers_ready_01_11.py").read_text(encoding="utf-8")
    assert "test_optional_live_integration_not_required" not in stub
    helper = (_TESTS / "tc05_live_fixtures.py").read_text(encoding="utf-8")
    assert "SUPABASE_URL / SUPABASE_SERVICE_ROLE absent" in helper
    assert "optional live_integration; live not required" not in helper


def test_cleanup_prefix_lock_and_test_live_target() -> None:
    helper = (_TESTS / "tc05_live_fixtures.py").read_text(encoding="utf-8")
    assert "tc05-" in helper
    makefile = _MAKEFILE.read_text(encoding="utf-8")
    assert "test-live:" in makefile
    assert '-m live_integration' in makefile or "-m live_integration" in makefile


def test_ac_thr_01_no_new_public_routes() -> None:
    assert _asgi_paths() == ["/health", "/ready"]
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment", "/thread"):
        assert f'@app.get("{name}' not in asgi
        assert f'@app.post("{name}' not in asgi
