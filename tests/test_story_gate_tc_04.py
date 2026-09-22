"""t04 — STORY-THREADS-TC-04 story gate: C-GW/C-ME TRACEABILITY + AC-THR-01."""

from __future__ import annotations

from pathlib import Path

from core.api.asgi_app import app
from core.domain.story_narrative import FORBIDDEN_STORY_KEYS
from tc04_traceability import TC04_ISSUE_IDS, TC04_ME_IDS, TC04_SCENARIO_IDS, TC04_SETTINGS_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_TC04_FILES = (
    _TESTS / "tc04_traceability.py",
    _TESTS / "tc04_httpx_fixtures.py",
    _TESTS / "test_tc04_issue_get_edges.py",
    _TESTS / "test_tc04_shell_settings_edges.py",
    _TESTS / "test_tc04_me_edges.py",
    _TESTS / "test_story_gate_tc_04.py",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_all_c_gw_c_me_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC04_FILES)
    missing = sorted(item for item in TC04_SCENARIO_IDS if item not in corpus)
    assert missing == []
    assert TC04_ISSUE_IDS <= TC04_SCENARIO_IDS
    assert TC04_SETTINGS_IDS <= TC04_SCENARIO_IDS
    assert TC04_ME_IDS <= TC04_SCENARIO_IDS
    families = set()
    for item in TC04_SCENARIO_IDS:
        if item.startswith("C-GW-ISS-"):
            families.add("ISS")
        elif item.startswith("C-GW-SET-"):
            families.add("SET")
        elif item.startswith("C-ME-"):
            families.add("ME")
    assert families == {"ISS", "SET", "ME"}


def test_forbidden_story_keys_matrix_complete() -> None:
    expected = {f"C-GW-SET-forbidden-{key}" for key in FORBIDDEN_STORY_KEYS}
    assert expected <= TC04_SETTINGS_IDS
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC04_FILES)
    missing = sorted(item for item in expected if item not in corpus)
    assert missing == []
    assert len(FORBIDDEN_STORY_KEYS) == 7


def test_phone_only_scenario_present() -> None:
    assert "C-ME-phone-only" in TC04_ME_IDS
    me = (_TESTS / "test_tc04_me_edges.py").read_text(encoding="utf-8")
    assert "phone_verified" in me
    assert "C-ME-phone-only" in me


def test_ac_thr_01_no_new_public_routes() -> None:
    assert _asgi_paths() == ["/health", "/ready"]
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment", "/thread"):
        assert f'@app.get("{name}' not in asgi
        assert f'@app.post("{name}' not in asgi
    impl = "\n".join(
        path.read_text(encoding="utf-8")
        for path in _TC04_FILES
        if path.name != "test_story_gate_tc_04.py"
    )
    assert "@pytest.mark.live_integration" not in impl
