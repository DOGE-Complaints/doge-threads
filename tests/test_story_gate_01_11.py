"""STORY-THREADS-01-11: persist wave gate — supabase wire; in_memory proofs; AC-THR-01."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from core.config import AppConfig
from core.infrastructure.db_supabase import REQUIRED_READINESS_TABLES
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from core.infrastructure.providers import provide_service_factory

_SRC = Path(__file__).resolve().parents[1] / "src"
_PROVIDERS = _SRC / "core" / "infrastructure" / "providers.py"
_DB = _SRC / "core" / "infrastructure" / "db_supabase.py"
_ASGI = _SRC / "core" / "api" / "asgi_app.py"
_OPS = Path(__file__).resolve().parents[1] / "supabase" / "migrations" / "README.md"


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_readiness_set_and_ops_note() -> None:
    assert REQUIRED_READINESS_TABLES == frozenset(
        {
            "thread_threads",
            "thread_comments",
            "thread_reaction_marks",
            "thread_attachment_refs",
        }
    )
    db_text = _DB.read_text(encoding="utf-8")
    for name in REQUIRED_READINESS_TABLES:
        assert name in db_text
    ops = _OPS.read_text(encoding="utf-8")
    assert "DB_BACKEND=supabase" in ops
    assert "migrations" in ops.lower()


def test_in_memory_proofs_intact(app_config: AppConfig) -> None:
    factory = provide_service_factory(app_config)
    assert isinstance(factory.discussion_store, InMemoryDiscussionStore)
    orchestrator = factory.write_orchestrator
    assert isinstance(orchestrator._reactions, InMemoryReactionMarksStore)
    assert isinstance(orchestrator._attachments, InMemoryAttachmentRefStore)
    providers = _PROVIDERS.read_text(encoding="utf-8")
    assert "InMemoryDiscussionStore" in providers
    assert "SupabaseDiscussionStore" in providers
    assert "SupabaseReactionMarksStore" in providers
    assert "SupabaseAttachmentRefStore" in providers


def test_ac_thr_01_no_new_public_http() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = _ASGI.read_text(encoding="utf-8")
    assert '@app.put("/threads' not in asgi
    assert '@app.post("/threads/issues/{issue_id}/attachment-refs' not in asgi
    assert "CREATE TABLE" not in asgi
