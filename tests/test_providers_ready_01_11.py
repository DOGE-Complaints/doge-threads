"""STORY-THREADS-01-11: supabase wire, readiness fail-closed, persist contract stub."""

from __future__ import annotations

from typing import Any

import pytest

from core.api.dependencies import ApiDependencies
from core.api.handlers import handle_readiness
from core.config import load_config_from_env
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from core.infrastructure.db_supabase import REQUIRED_READINESS_TABLES, SupabaseDatabase
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from core.infrastructure.providers import provide_service_factory
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore


def _supabase_config():
    return load_config_from_env(
        {
            "APP_PROFILE": "demo",
            "DB_BACKEND": "supabase",
            "SUPABASE_URL": "http://example.test",
            "SUPABASE_SERVICE_ROLE": "test-role",
        }
    )


def test_required_readiness_tables_are_four_thread_names() -> None:
    assert REQUIRED_READINESS_TABLES == frozenset(
        {
            "thread_threads",
            "thread_comments",
            "thread_reaction_marks",
            "thread_attachment_refs",
        }
    )


def test_required_tables_ready_false_on_probe_fail() -> None:
    db = SupabaseDatabase(base_url="http://example.test", service_role_key="test-role")

    def _boom(**kwargs: Any) -> Any:
        del kwargs
        raise RuntimeError("missing table")

    db._request = _boom  # type: ignore[method-assign]
    assert db.required_tables_ready() is False


def test_in_memory_factory_keeps_in_memory_stores(app_config) -> None:
    factory = provide_service_factory(app_config)
    assert factory.db_backend == "in_memory"
    assert isinstance(factory.discussion_store, InMemoryDiscussionStore)
    orchestrator = factory.write_orchestrator
    assert isinstance(orchestrator._reactions, InMemoryReactionMarksStore)
    assert isinstance(orchestrator._attachments, InMemoryAttachmentRefStore)


def test_supabase_factory_wires_postgrest_stores(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(SupabaseDatabase, "required_tables_ready", lambda self: True)
    factory = provide_service_factory(_supabase_config())
    assert factory.db_backend == "supabase"
    assert factory.db_ready is True
    assert isinstance(factory.discussion_store, SupabaseDiscussionStore)
    orchestrator = factory.write_orchestrator
    assert isinstance(orchestrator._reactions, SupabaseReactionMarksStore)
    assert isinstance(orchestrator._attachments, SupabaseAttachmentRefStore)
    assert orchestrator._discussion is factory.discussion_store


def test_missing_tables_db_ready_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(SupabaseDatabase, "required_tables_ready", lambda self: False)
    factory = provide_service_factory(_supabase_config())
    assert factory.db_ready is False
    assert factory.db_checks["credentials"] is True
    assert factory.db_checks["tables"] is False
    assert isinstance(factory.discussion_store, SupabaseDiscussionStore)


def test_ready_degraded_when_tables_missing() -> None:
    deps = ApiDependencies(
        config=_supabase_config(),
        db_backend="supabase",
        db_ready=False,
        db_checks={"credentials": True, "tables": False},
    )
    payload = handle_readiness(deps, trace_id="t-ready")
    assert payload["data"]["status"] == "degraded"
    assert payload["data"]["db"]["ready"] is False
    assert payload["data"]["db"]["backend"] == "supabase"
    assert payload["data"]["db"]["checks"]["tables"] is False


class _SharedFake:
    def __init__(self) -> None:
        self.threads: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.marks: list[dict[str, Any]] = []

    def _eq(self, params: dict[str, str], name: str) -> str | None:
        raw = params.get(name)
        if raw is None or raw == "is.null":
            return None
        return raw.removeprefix("eq.")

    def _request(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json_body: Any = None,
        prefer: str | None = None,
    ) -> Any:
        del prefer
        params = params or {}
        if path == "/rest/v1/thread_threads":
            if method == "GET":
                key = (
                    self._eq(params, "node") or "",
                    self._eq(params, "entity_type") or "",
                    self._eq(params, "entity_id") or "",
                )
                row = self.threads.get(key)
                return [row] if row is not None else []
            if method == "POST":
                row = dict(json_body)
                self.threads[(row["node"], row["entity_type"], row["entity_id"])] = row
                return [row]
        if path == "/rest/v1/thread_reaction_marks":
            if method == "GET":
                return [
                    item
                    for item in self.marks
                    if item["node"] == self._eq(params, "node")
                    and item["entity_type"] == self._eq(params, "entity_type")
                    and item["entity_id"] == self._eq(params, "entity_id")
                    and item["target_kind"] == self._eq(params, "target_kind")
                    and item.get("comment_id") == self._eq(params, "comment_id")
                ]
            if method == "POST":
                row = dict(json_body)
                self.marks.append(row)
                return [row]
        raise AssertionError(f"unexpected {method} {path}")


def test_persist_roundtrip_survives_new_client() -> None:
    """Write via one store; a new client reading the same stub rows still sees them."""
    shared = _SharedFake()
    knobs = FixedThreadKnobs(max_depth=4, max_reactions_per_actor=3)
    writer_db = SupabaseDatabase(base_url="http://example.test", service_role_key="role-a")
    writer_db._request = shared._request  # type: ignore[method-assign]
    writer = SupabaseDiscussionStore(db=writer_db, knobs=knobs)
    marks_writer = SupabaseReactionMarksStore(db=writer_db, knobs=knobs)
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    writer.attach_thread(key)
    target = ReactionTarget(kind="thread_root", thread_key=key)
    marks_writer.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="acknowledge"))

    reader_db = SupabaseDatabase(base_url="http://example.test", service_role_key="role-b")
    reader_db._request = shared._request  # type: ignore[method-assign]
    reader = SupabaseDiscussionStore(db=reader_db, knobs=knobs)
    marks_reader = SupabaseReactionMarksStore(db=reader_db, knobs=knobs)
    assert reader.get_thread(key) is not None
    listed = marks_reader.list_marks(target)
    assert [item.reaction_id for item in listed] == ["acknowledge"]

