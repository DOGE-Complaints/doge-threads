"""t05 — STORY-THREADS-TC-02 story gate: O-* TRACEABILITY, G2 stub, AC-THR-01."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore
from tc02_orch_fixtures import make_orch_harness
from tc02_traceability import TC02_SCENARIO_IDS

_TESTS = Path(__file__).resolve().parent
_SRC_ROOT = _TESTS.parent / "src"
_TC02_FILES = (
    _TESTS / "tc02_traceability.py",
    _TESTS / "tc02_orch_fixtures.py",
    _TESTS / "test_tc02_fixture_and_write_matrix.py",
    _TESTS / "test_tc02_deny_enforce_order.py",
    _TESTS / "test_story_gate_tc_02.py",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_all_o_scenario_ids_present_for_traceability() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in _TC02_FILES)
    missing = sorted(item for item in TC02_SCENARIO_IDS if item not in corpus)
    assert missing == []
    families = {item.split("-", 2)[1] for item in TC02_SCENARIO_IDS}
    assert families == {"WR", "DENY", "ENF", "ORD"}


def test_g2_stub_half_wires_supabase_stores() -> None:
    harness = make_orch_harness(backend="supabase_stub", verified=True)
    assert isinstance(harness.discussion, SupabaseDiscussionStore)
    assert isinstance(harness.reactions, SupabaseReactionMarksStore)
    assert isinstance(harness.attachments, SupabaseAttachmentRefStore)
    assert harness.fake is not None


def test_ac_thr_01_no_new_public_routes() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment"):
        assert f'@app.get("{name}' not in asgi
        assert f'@app.post("{name}' not in asgi
