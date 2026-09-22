"""STORY-THREADS-01-10: PostgREST marks/refs with stubbed transport."""

from __future__ import annotations

from typing import Any

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import LegalFloorError, MediaTypeNotAllowedError, ReactionMutexError
from core.domain.knobs import FixedThreadKnobs
from core.domain.media_floor import StubLegalMediaFloor
from core.domain.reaction_catalog import CATALOG_REACTION_IDS
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_marks_mappers import MARK_WRITE_COLUMNS, mark_to_row
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore
from core.infrastructure.supabase_refs_mappers import REF_WRITE_COLUMNS, ref_to_row


class _RecordingFloor(StubLegalMediaFloor):
    def __init__(self) -> None:
        self.seen: list[str] = []

    def honour(self, ref: AttachmentRef) -> None:
        self.seen.append(ref.ref_id)
        super().honour(ref)


class _FakePostgrest:
    def __init__(self) -> None:
        self.marks: list[dict[str, Any]] = []
        self.refs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, str]] = []

    def _eq(self, params: dict[str, str], name: str) -> str | None:
        raw = params.get(name)
        if raw is None:
            return None
        if raw == "is.null":
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
        self.calls.append((method, path))
        params = params or {}
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
        if path == "/rest/v1/thread_attachment_refs":
            if method == "GET":
                comment_id = self._eq(params, "comment_id")
                return [item for item in self.refs if item["comment_id"] == comment_id]
            if method == "POST":
                row = dict(json_body)
                self.refs.append(row)
                return [row]
        raise AssertionError(f"unexpected {method} {path}")


def _db() -> tuple[SupabaseDatabase, _FakePostgrest]:
    fake = _FakePostgrest()
    db = SupabaseDatabase(base_url="http://example.test", service_role_key="test-role")
    db._request = fake._request  # type: ignore[method-assign]
    return db, fake


def _root() -> ReactionTarget:
    return ReactionTarget(
        kind="thread_root",
        thread_key=ThreadKey(node="n1", entity_type="Issue", entity_id="e1"),
    )


def test_mappers_use_01_08_columns_only() -> None:
    mark = ReactionMark(actor_id="a1", target=_root(), reaction_id="acknowledge")
    mark_row = mark_to_row(mark)
    assert set(mark_row) == MARK_WRITE_COLUMNS
    assert "created_at" not in mark_row
    ref = AttachmentRef(ref_id="r1", media_type="image/png", comment_id="c1")
    ref_row = ref_to_row(ref)
    assert set(ref_row) == REF_WRITE_COLUMNS
    assert "created_at" not in ref_row


def test_mark_roundtrip_and_catalog_id() -> None:
    db, fake = _db()
    store = SupabaseReactionMarksStore(
        db=db, knobs=FixedThreadKnobs(max_depth=4, max_reactions_per_actor=3)
    )
    stored = store.add_mark(ReactionMark(actor_id="a1", target=_root(), reaction_id="acknowledge"))
    assert stored.reaction_id == "acknowledge"
    assert stored.reaction_id in CATALOG_REACTION_IDS
    assert store.list_marks(_root()) == [stored]
    assert all(path.endswith("thread_reaction_marks") for _, path in fake.calls)


def test_agree_disagree_mutex_stays_in_domain() -> None:
    db, fake = _db()
    store = SupabaseReactionMarksStore(
        db=db, knobs=FixedThreadKnobs(max_depth=4, max_reactions_per_actor=3)
    )
    target = ReactionTarget(
        kind="comment",
        thread_key=ThreadKey(node="n1", entity_type="Issue", entity_id="e1"),
        comment_id="c1",
    )
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="agree"))
    with pytest.raises(ReactionMutexError):
        store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="disagree"))
    assert [item.reaction_id for item in store.list_marks(target)] == ["agree"]
    assert not any(call[0] == "POST" and call[1].endswith("disagree") for call in fake.calls)


def test_ref_roundtrip() -> None:
    db, fake = _db()
    store = SupabaseAttachmentRefStore(
        db=db,
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=("image/png",)),
    )
    stored = store.accept_ref(
        AttachmentRef(ref_id="blob://ok", media_type="image/png", comment_id="c1")
    )
    assert store.list_refs("c1") == [stored]
    assert all(path.endswith("thread_attachment_refs") for _, path in fake.calls)


def test_floor_then_allowlist_reject_before_persist() -> None:
    db, fake = _db()
    floor = _RecordingFloor()
    store = SupabaseAttachmentRefStore(
        db=db,
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=("image/png",)),
        floor=floor,
    )
    with pytest.raises(LegalFloorError):
        store.accept_ref(
            AttachmentRef(
                ref_id="blob://blocked",
                media_type="image/png",
                comment_id="c1",
                floor_class="catastrophic",
            )
        )
    assert floor.seen == ["blob://blocked"]
    assert store.list_refs("c1") == []
    assert not any(method == "POST" for method, _ in fake.calls)
    with pytest.raises(MediaTypeNotAllowedError):
        store.accept_ref(
            AttachmentRef(ref_id="blob://gif", media_type="image/gif", comment_id="c1")
        )
    assert store.list_refs("c1") == []
