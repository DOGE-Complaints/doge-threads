from __future__ import annotations

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


class InMemoryReactionMarksStore:
    """In-process marks store. No SQL / column lists / public path."""

    def __init__(self, knobs: ThreadKnobs) -> None:
        self._knobs = knobs
        self._marks: list[ReactionMark] = []

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
        self._marks.append(mark)
        return mark

    def remove_mark(self, mark: ReactionMark) -> None:
        self._marks = [
            item
            for item in self._marks
            if not (
                item.actor_id == mark.actor_id
                and item.target == mark.target
                and item.reaction_id == mark.reaction_id
            )
        ]

    def list_marks(self, target: ReactionTarget) -> list[ReactionMark]:
        return [item for item in self._marks if item.target == target]

    def _enabled(self, reaction_id: str) -> bool:
        enable = self._knobs.reactions_enable
        if not enable:
            return True
        return enable.get(reaction_id) is True

    def _actor_marks(self, actor_id: str, target: ReactionTarget) -> list[ReactionMark]:
        return [
            item
            for item in self._marks
            if item.actor_id == actor_id and item.target == target
        ]
