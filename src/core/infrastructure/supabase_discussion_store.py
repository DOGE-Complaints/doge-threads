"""PostgREST DiscussionStore on `thread_threads` / `thread_comments`."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from core.domain.comment import Comment
from core.domain.errors import CommentNotFoundError, DepthExceededError, ThreadNotFoundError
from core.domain.ports import ThreadKnobs
from core.domain.thread_key import Thread, ThreadKey
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.in_memory_discussion_store import CivicSideEffects
from core.infrastructure.supabase_discussion_mappers import (
    COMMENT_TABLE,
    THREAD_TABLE,
    comment_from_row,
    comment_to_row,
    thread_from_row,
    thread_to_row,
)


class SupabaseDiscussionStore:
    """DiscussionStore via existing SupabaseDatabase. No civic / Story writes."""

    def __init__(self, db: SupabaseDatabase, knobs: ThreadKnobs) -> None:
        self._db = db
        self._knobs = knobs
        self.civic_side_effects = CivicSideEffects()

    @property
    def knobs(self) -> ThreadKnobs:
        return self._knobs

    def attach_thread(self, key: ThreadKey) -> Thread:
        existing = self.get_thread(key)
        if existing is not None:
            return existing
        payload = self._db._request(
            method="POST",
            path=f"/rest/v1/{THREAD_TABLE}",
            json_body=thread_to_row(Thread(key=key)),
            prefer="return=representation",
        )
        row = _first_row(payload)
        if row is None:
            return Thread(key=key)
        return thread_from_row(row)

    def get_thread(self, key: ThreadKey) -> Thread | None:
        payload = self._db._request(
            method="GET",
            path=f"/rest/v1/{THREAD_TABLE}",
            params={
                "select": "node,entity_type,entity_id",
                "node": f"eq.{key.node}",
                "entity_type": f"eq.{key.entity_type}",
                "entity_id": f"eq.{key.entity_id}",
                "limit": "1",
            },
        )
        row = _first_row(payload)
        if row is None:
            return None
        return thread_from_row(row)

    def create_comment(
        self,
        key: ThreadKey,
        body: str,
        *,
        parent_id: str | None = None,
    ) -> Comment:
        if self.get_thread(key) is None:
            raise ThreadNotFoundError(f"thread not attached: {key}")
        depth = 1
        if parent_id is not None:
            parent = self._find_comment(key, parent_id)
            if parent is None:
                raise CommentNotFoundError(f"parent comment not found: {parent_id}")
            depth = parent.depth + 1
        if depth > self._knobs.max_depth:
            raise DepthExceededError(depth, self._knobs.max_depth)
        comment = Comment(
            comment_id=uuid4().hex,
            thread_key=key,
            parent_id=parent_id,
            body=body,
            depth=depth,
        )
        payload = self._db._request(
            method="POST",
            path=f"/rest/v1/{COMMENT_TABLE}",
            json_body=comment_to_row(comment),
            prefer="return=representation",
        )
        row = _first_row(payload)
        if row is None:
            return comment
        return comment_from_row(row)

    def list_comments(self, key: ThreadKey) -> list[Comment]:
        payload = self._db._request(
            method="GET",
            path=f"/rest/v1/{COMMENT_TABLE}",
            params={
                "select": "comment_id,node,entity_type,entity_id,parent_id,body,depth",
                "node": f"eq.{key.node}",
                "entity_type": f"eq.{key.entity_type}",
                "entity_id": f"eq.{key.entity_id}",
                "order": "created_at.asc",
            },
        )
        rows = _as_rows(payload)
        return [comment_from_row(row) for row in rows]

    def _find_comment(self, key: ThreadKey, comment_id: str) -> Comment | None:
        payload = self._db._request(
            method="GET",
            path=f"/rest/v1/{COMMENT_TABLE}",
            params={
                "select": "comment_id,node,entity_type,entity_id,parent_id,body,depth",
                "comment_id": f"eq.{comment_id}",
                "node": f"eq.{key.node}",
                "entity_type": f"eq.{key.entity_type}",
                "entity_id": f"eq.{key.entity_id}",
                "limit": "1",
            },
        )
        row = _first_row(payload)
        if row is None:
            return None
        return comment_from_row(row)


def _as_rows(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []


def _first_row(payload: Any) -> dict[str, Any] | None:
    rows = _as_rows(payload)
    if not rows:
        return None
    return rows[0]
