"""STORY-THREADS-01-08: four thread_* tables in shared-public migration; AC-THR-01."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app

_MIGRATIONS = Path(__file__).resolve().parents[1] / "supabase" / "migrations"
_SQL = _MIGRATIONS / "202609220919_threads_01_08_shell_tables.sql"
_TABLES = (
    "thread_threads",
    "thread_comments",
    "thread_reaction_marks",
    "thread_attachment_refs",
)
_CIVIC_TOKENS = (
    "create table if not exists public.story",
    "create table if not exists public.stories",
    "create table if not exists public.cluster",
    "create table if not exists public.issues",
    "create table if not exists public.doge_issues",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def test_four_thread_tables_exist_in_migration() -> None:
    text = _SQL.read_text(encoding="utf-8")
    for name in _TABLES:
        assert f"create table if not exists public.{name}" in text
        assert f"{name}_service_role_all" in text
        assert f"alter table public.{name} enable row level security;" in text


def test_columns_are_domain_plus_created_at() -> None:
    text = _SQL.read_text(encoding="utf-8")
    assert "primary key (node, entity_type, entity_id)" in text
    assert "comment_id text primary key" in text
    assert "parent_id text," in text
    assert "target_kind text not null" in text
    assert "reaction_id text not null" in text
    assert "floor_class text not null" in text
    assert "created_at timestamptz not null default now()" in text
    assert "voice_weight" not in text
    assert "payload_json" not in text
    for token in _CIVIC_TOKENS:
        assert token not in text


def test_ac_thr_01_ddl_is_not_public_http() -> None:
    assert _asgi_paths() == CURRENT_PUBLIC_GET_PATHS
    asgi = (
        Path(__file__).resolve().parents[1] / "src" / "core" / "api" / "asgi_app.py"
    ).read_text(encoding="utf-8")
    assert '@app.put("/threads/issues/{issue_id}/reactions")' in asgi
    assert '@app.put("/threads/by-issue' not in asgi
    assert '@app.post("/threads/issues/{issue_id}/attachment-refs' not in asgi
    assert "create table" not in asgi
