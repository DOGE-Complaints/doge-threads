"""STORY-THREADS-01-09: PostgREST DiscussionStore with stubbed transport."""

from __future__ import annotations

from typing import Any

import pytest

from core.domain.comment import Comment
from core.domain.errors import DepthExceededError
from core.domain.knobs import FixedThreadKnobs
from core.domain.thread_key import Thread, ThreadKey
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.supabase_discussion_mappers import (
    COMMENT_WRITE_COLUMNS,
    THREAD_WRITE_COLUMNS,
    comment_from_row,
    comment_to_row,
    thread_from_row,
    thread_to_row,
)
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore

_CIVIC_PATH_TOKENS = ("/stories", "/story", "/cluster", "/issues", "/doge_issues")


class _FakePostgrest:
    def __init__(self) -> None:
        self.threads: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.comments: list[dict[str, Any]] = []
        self.calls: list[tuple[str, str]] = []

    def _eq(self, params: dict[str, str], name: str) -> str | None:
        raw = params.get(name)
        if raw is None:
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
        if any(token in path for token in _CIVIC_PATH_TOKENS):
            raise AssertionError(f"civic path forbidden: {path}")
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
                key = (row["node"], row["entity_type"], row["entity_id"])
                self.threads[key] = row
                return [row]
        if path == "/rest/v1/thread_comments":
            if method == "GET":
                comment_id = self._eq(params, "comment_id")
                if comment_id is not None:
                    return [
                        item
                        for item in self.comments
                        if item["comment_id"] == comment_id
                        and item["node"] == self._eq(params, "node")
                        and item["entity_type"] == self._eq(params, "entity_type")
                        and item["entity_id"] == self._eq(params, "entity_id")
                    ]
                return [
                    item
                    for item in self.comments
                    if item["node"] == self._eq(params, "node")
                    and item["entity_type"] == self._eq(params, "entity_type")
                    and item["entity_id"] == self._eq(params, "entity_id")
                ]
            if method == "POST":
                row = dict(json_body)
                self.comments.append(row)
                return [row]
        raise AssertionError(f"unexpected {method} {path}")


def _store() -> tuple[SupabaseDiscussionStore, _FakePostgrest]:
    fake = _FakePostgrest()
    db = SupabaseDatabase(base_url="http://example.test", service_role_key="test-role")
    db._request = fake._request  # type: ignore[method-assign]
    return SupabaseDiscussionStore(db=db, knobs=FixedThreadKnobs(max_depth=2)), fake


def test_mappers_use_01_08_columns_only() -> None:
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    thread_row = thread_to_row(Thread(key=key))
    assert set(thread_row) == THREAD_WRITE_COLUMNS
    parsed = thread_from_row({**thread_row, "created_at": "2026-09-22T09:00:00Z"})
    assert parsed.key == key
    comment = Comment(
        comment_id="c1",
        thread_key=key,
        parent_id=None,
        body="hello",
        depth=1,
    )
    comment_row = comment_to_row(comment)
    assert set(comment_row) == COMMENT_WRITE_COLUMNS
    assert "created_at" not in comment_row
    assert comment_from_row({**comment_row, "created_at": "now"}).comment_id == "c1"


def test_attach_create_list_nested_comments() -> None:
    store, fake = _store()
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    attached = store.attach_thread(key)
    assert attached.key == key
    assert store.get_thread(key) == attached
    root = store.create_comment(key, "root")
    child = store.create_comment(key, "child", parent_id=root.comment_id)
    listed = store.list_comments(key)
    assert [item.body for item in listed] == ["root", "child"]
    assert child.depth == 2
    assert all(path.endswith(("thread_threads", "thread_comments")) for _, path in fake.calls)


def test_depth_exceeded_rejected() -> None:
    store, _fake = _store()
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    store.attach_thread(key)
    root = store.create_comment(key, "root")
    child = store.create_comment(key, "child", parent_id=root.comment_id)
    with pytest.raises(DepthExceededError) as exc:
        store.create_comment(key, "too deep", parent_id=child.comment_id)
    assert exc.value.depth == 3
    assert exc.value.max_depth == 2
    assert [item.body for item in store.list_comments(key)] == ["root", "child"]


def test_comment_create_does_not_mutate_story_or_cluster() -> None:
    store, fake = _store()
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    store.attach_thread(key)
    store.create_comment(key, "hello")
    effects = store.civic_side_effects
    assert effects.story_creates == []
    assert effects.story_mutations == []
    assert effects.cluster_mutations == []
    assert "create_story" not in dir(store)
    assert "create_cluster" not in dir(store)
    assert "mutate_cluster" not in dir(store)
    assert all(
        not any(token in path for token in _CIVIC_PATH_TOKENS) for _, path in fake.calls
    )
