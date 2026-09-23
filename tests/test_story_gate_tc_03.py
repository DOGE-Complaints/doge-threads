"""t06 — STORY-THREADS-TC-03 story gate: C-PG-* TRACEABILITY, G3 stub, AC-THR-01."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from tc03_fake_postgrest import CIVIC_PATH_TOKENS, FakeContractPostgrest
from tc03_traceability import TC03_SCENARIO_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_TC03_FILES = (
    _TESTS / "tc03_traceability.py",
    _TESTS / "tc03_fake_postgrest.py",
    _TESTS / "test_tc03_get_filters.py",
    _TESTS / "test_tc03_dup_and_http.py",
    _TESTS / "test_tc03_malformed_civic_map.py",
    _TESTS / "test_story_gate_tc_03.py",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_all_c_pg_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC03_FILES)
    missing = sorted(item for item in TC03_SCENARIO_IDS if item not in corpus)
    assert missing == []
    families = {item.split("-", 3)[2] for item in TC03_SCENARIO_IDS}
    assert families == {"GET", "DUP", "HTTP", "BAD", "MAP"}


def test_g3_stub_fake_has_unique_and_civic() -> None:
    fake = FakeContractPostgrest()
    assert hasattr(fake, "_mark_unique")
    assert CIVIC_PATH_TOKENS


def test_ac_thr_01_no_new_public_routes() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment"):
        assert f'@app.get("{name}' not in asgi
        assert f'@app.post("{name}' not in asgi
