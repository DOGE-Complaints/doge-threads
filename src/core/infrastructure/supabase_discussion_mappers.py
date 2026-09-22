"""Map Thread/Comment ↔ PostgREST JSON using 01-08 columns only."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.domain.comment import Comment
from core.domain.thread_key import Thread, ThreadKey

THREAD_TABLE = "thread_threads"
COMMENT_TABLE = "thread_comments"

THREAD_WRITE_COLUMNS: frozenset[str] = frozenset({"node", "entity_type", "entity_id"})
COMMENT_WRITE_COLUMNS: frozenset[str] = frozenset(
    {
        "comment_id",
        "node",
        "entity_type",
        "entity_id",
        "parent_id",
        "body",
        "depth",
    }
)


def thread_to_row(thread: Thread) -> dict[str, str]:
    """Serialize a thread to `thread_threads` columns (no `created_at` write)."""
    row = {
        "node": thread.key.node,
        "entity_type": thread.key.entity_type,
        "entity_id": thread.key.entity_id,
    }
    extra = set(row) - THREAD_WRITE_COLUMNS
    if extra:
        raise ValueError(f"thread row invented columns: {sorted(extra)}")
    return row


def thread_from_row(row: Mapping[str, Any]) -> Thread:
    """Parse a `thread_threads` row. Extra keys (e.g. `created_at`) are ignored."""
    return Thread(
        key=ThreadKey(
            node=str(row["node"]),
            entity_type=str(row["entity_type"]),
            entity_id=str(row["entity_id"]),
        )
    )


def comment_to_row(comment: Comment) -> dict[str, Any]:
    """Serialize a comment to `thread_comments` columns (no `created_at` write)."""
    row: dict[str, Any] = {
        "comment_id": comment.comment_id,
        "node": comment.thread_key.node,
        "entity_type": comment.thread_key.entity_type,
        "entity_id": comment.thread_key.entity_id,
        "parent_id": comment.parent_id,
        "body": comment.body,
        "depth": comment.depth,
    }
    extra = set(row) - COMMENT_WRITE_COLUMNS
    if extra:
        raise ValueError(f"comment row invented columns: {sorted(extra)}")
    return row


def comment_from_row(row: Mapping[str, Any]) -> Comment:
    """Parse a `thread_comments` row. Extra keys (e.g. `created_at`) are ignored."""
    parent_raw = row.get("parent_id")
    parent_id = None if parent_raw is None else str(parent_raw)
    return Comment(
        comment_id=str(row["comment_id"]),
        thread_key=ThreadKey(
            node=str(row["node"]),
            entity_type=str(row["entity_type"]),
            entity_id=str(row["entity_id"]),
        ),
        parent_id=parent_id,
        body=str(row["body"]),
        depth=int(row["depth"]),
    )
