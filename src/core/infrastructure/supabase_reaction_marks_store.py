"""PostgREST ReactionMarksStore on `thread_reaction_marks`."""

from __future__ import annotations

from typing import Any

from core.domain.errors import (
    MaxReactionsExceededError,
    ReactionDisabledError,
    ReactionLayerError,
    ReactionMutexError,
    UnknownReactionIdError,
)
from core.domain.ports import ThreadKnobs
from core.domain.reaction_catalog import (
    CATALOG_REACTION_IDS,
    MODERATION_REACTION_IDS,
    MUTEX_PAIRS,
)
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.supabase_marks_mappers import MARKS_TABLE, mark_from_row, mark_to_row


class SupabaseReactionMarksStore:
    """ReactionMarksStore via existing SupabaseDatabase. Domain rules stay in Python."""

    def __init__(self, db: SupabaseDatabase, knobs: ThreadKnobs) -> None:
        self._db = db
        self._knobs = knobs

    @property
    def knobs(self) -> ThreadKnobs:
        return self._knobs

    def add_mark(self, mark: ReactionMark) -> ReactionMark:
        if mark.reaction_id not in CATALOG_REACTION_IDS:
            raise UnknownReactionIdError(f"unknown reaction_id: {mark.reaction_id}")
        if not self._enabled(mark.reaction_id):
            raise ReactionDisabledError(f"reaction_id disabled: {mark.reaction_id}")
        if mark.reaction_id in MODERATION_REACTION_IDS and mark.target.kind == "thread_root":
            raise ReactionLayerError("moderation marks are comments-only")
        existing = self._actor_marks(mark.actor_id, mark.target)
        counterpart = MUTEX_PAIRS.get(mark.reaction_id)
        if counterpart is not None and any(item.reaction_id == counterpart for item in existing):
            raise ReactionMutexError(
                f"{mark.reaction_id} conflicts with {counterpart} on the same target"
            )
        for item in existing:
            if item.reaction_id == mark.reaction_id:
                return item
        if len(existing) >= self._knobs.max_reactions_per_actor:
            raise MaxReactionsExceededError(
                f"max_reactions_per_actor {self._knobs.max_reactions_per_actor} exceeded"
            )
        payload = self._db._request(
            method="POST",
            path=f"/rest/v1/{MARKS_TABLE}",
            json_body=mark_to_row(mark),
            prefer="return=representation",
        )
        row = _first_row(payload)
        if row is None:
            return mark
        return mark_from_row(row)

    def list_marks(self, target: ReactionTarget) -> list[ReactionMark]:
        params: dict[str, str] = {
            "select": "actor_id,node,entity_type,entity_id,target_kind,comment_id,reaction_id",
            "node": f"eq.{target.thread_key.node}",
            "entity_type": f"eq.{target.thread_key.entity_type}",
            "entity_id": f"eq.{target.thread_key.entity_id}",
            "target_kind": f"eq.{target.kind}",
            "order": "created_at.asc",
        }
        if target.comment_id is None:
            params["comment_id"] = "is.null"
        else:
            params["comment_id"] = f"eq.{target.comment_id}"
        payload = self._db._request(
            method="GET",
            path=f"/rest/v1/{MARKS_TABLE}",
            params=params,
        )
        return [mark_from_row(row) for row in _as_rows(payload)]

    def _enabled(self, reaction_id: str) -> bool:
        enable = self._knobs.reactions_enable
        if not enable:
            return True
        return enable.get(reaction_id) is True

    def _actor_marks(self, actor_id: str, target: ReactionTarget) -> list[ReactionMark]:
        return [item for item in self.list_marks(target) if item.actor_id == actor_id]


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
