"""STORY-THREADS-01-09: PostgREST discussion store; AC-THR-01/02; in_memory kept."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from core.config import AppConfig
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.providers import provide_service_factory
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore

_SRC = Path(__file__).resolve().parents[1] / "src"
_STORE = _SRC / "core" / "infrastructure" / "supabase_discussion_store.py"
_MAPPERS = _SRC / "core" / "infrastructure" / "supabase_discussion_mappers.py"
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


def test_supabase_discussion_store_exists() -> None:
    assert _STORE.is_file()
    assert _MAPPERS.is_file()
    text = _STORE.read_text(encoding="utf-8")
    assert "attach_thread" in text
    assert "create_comment" in text
    assert "list_comments" in text
    assert "thread_threads" in _MAPPERS.read_text(encoding="utf-8")
    assert "thread_comments" in _MAPPERS.read_text(encoding="utf-8")


def test_in_memory_store_kept_and_providers_unswitched(app_config: AppConfig) -> None:
    assert InMemoryDiscussionStore is not None
    factory = provide_service_factory(app_config)
    assert isinstance(factory.discussion_store, InMemoryDiscussionStore)
    providers = _PROVIDERS.read_text(encoding="utf-8")
    assert "InMemoryDiscussionStore" in providers
    assert "REQUIRED_READINESS_TABLES" not in providers


def test_ac_thr_01_no_new_public_http() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = _ASGI.read_text(encoding="utf-8")
    assert '@app.put("/threads' not in asgi
    assert '@app.post("/threads/issues/{issue_id}/attachment-refs' not in asgi
    assert "SupabaseDiscussionStore" not in asgi


def test_store_has_no_civic_writers() -> None:
    names = dir(SupabaseDiscussionStore)
    assert "create_story" not in names
    assert "mutate_cluster" not in names
    assert "create_cluster" not in names
