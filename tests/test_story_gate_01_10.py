"""STORY-THREADS-01-10: PostgREST marks/refs; AC-THR-01/03/08; in_memory kept."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from core.config import AppConfig
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from core.infrastructure.providers import provide_service_factory

_SRC = Path(__file__).resolve().parents[1] / "src"
_MARKS = _SRC / "core" / "infrastructure" / "supabase_reaction_marks_store.py"
_REFS = _SRC / "core" / "infrastructure" / "supabase_attachment_ref_store.py"
_PROVIDERS = _SRC / "core" / "infrastructure" / "providers.py"
_ASGI = _SRC / "core" / "api" / "asgi_app.py"


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_supabase_marks_and_refs_stores_exist() -> None:
    assert _MARKS.is_file()
    assert _REFS.is_file()
    marks = _MARKS.read_text(encoding="utf-8")
    refs = _REFS.read_text(encoding="utf-8")
    assert "add_mark" in marks
    assert "list_marks" in marks
    assert "thread_reaction_marks" in marks
    assert "accept_ref" in refs
    assert "list_refs" in refs
    assert "thread_attachment_refs" in refs
    assert "voice_weight" not in marks
    assert "voice_weight" not in refs
    assert "upload_bytes" not in refs


def test_in_memory_stores_kept_and_providers_unswitched(app_config: AppConfig) -> None:
    factory = provide_service_factory(app_config)
    orchestrator = factory.write_orchestrator
    assert isinstance(orchestrator._reactions, InMemoryReactionMarksStore)
    assert isinstance(orchestrator._attachments, InMemoryAttachmentRefStore)
    providers = _PROVIDERS.read_text(encoding="utf-8")
    assert "InMemoryReactionMarksStore" in providers
    assert "InMemoryAttachmentRefStore" in providers


def test_ac_thr_01_no_new_public_http() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = _ASGI.read_text(encoding="utf-8")
    assert '@app.put("/threads' not in asgi
    assert '@app.post("/threads/issues/{issue_id}/attachment-refs' not in asgi
    assert "SupabaseReactionMarksStore" not in asgi
    assert "SupabaseAttachmentRefStore" not in asgi
