"""Map ReactionMark ↔ PostgREST JSON using 01-08 columns only."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey

MARKS_TABLE = "thread_reaction_marks"
MARK_WRITE_COLUMNS: frozenset[str] = frozenset(
    {
        "actor_id",
        "node",
        "entity_type",
        "entity_id",
        "target_kind",
        "comment_id",
        "reaction_id",
    }
)


def mark_to_row(mark: ReactionMark) -> dict[str, Any]:
    """Serialize a mark to `thread_reaction_marks` (no `created_at` write)."""
    row: dict[str, Any] = {
        "actor_id": mark.actor_id,
        "node": mark.target.thread_key.node,
        "entity_type": mark.target.thread_key.entity_type,
        "entity_id": mark.target.thread_key.entity_id,
        "target_kind": mark.target.kind,
        "comment_id": mark.target.comment_id,
        "reaction_id": mark.reaction_id,
    }
    extra = set(row) - MARK_WRITE_COLUMNS
    if extra:
        raise ValueError(f"mark row invented columns: {sorted(extra)}")
    return row


def mark_from_row(row: Mapping[str, Any]) -> ReactionMark:
    """Parse a `thread_reaction_marks` row. Extra keys (e.g. `created_at`) ignored."""
    comment_raw = row.get("comment_id")
    comment_id = None if comment_raw is None else str(comment_raw)
    kind = str(row["target_kind"])
    if kind not in ("thread_root", "comment"):
        raise ValueError(f"unknown target_kind: {kind}")
    return ReactionMark(
        actor_id=str(row["actor_id"]),
        target=ReactionTarget(
            kind=kind,  # type: ignore[arg-type]
            thread_key=ThreadKey(
                node=str(row["node"]),
                entity_type=str(row["entity_type"]),
                entity_id=str(row["entity_id"]),
            ),
            comment_id=comment_id,
        ),
        reaction_id=str(row["reaction_id"]),
    )
