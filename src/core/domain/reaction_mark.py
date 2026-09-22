from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.domain.thread_key import ThreadKey

TargetKind = Literal["thread_root", "comment"]


@dataclass(frozen=True)
class ReactionTarget:
    """Mark target: thread root or a comment. No HTTP / DDL schema."""

    kind: TargetKind
    thread_key: ThreadKey
    comment_id: str | None = None

    def __post_init__(self) -> None:
        if self.kind == "comment" and not (self.comment_id and self.comment_id.strip()):
            raise ValueError("comment target requires comment_id")
        if self.kind == "thread_root" and self.comment_id is not None:
            raise ValueError("thread_root target must not set comment_id")


@dataclass(frozen=True)
class ReactionMark:
    """Actor × target × catalog reaction_id (reactions.v1)."""

    actor_id: str
    target: ReactionTarget
    reaction_id: str

    def __post_init__(self) -> None:
        if not self.actor_id.strip():
            raise ValueError("actor_id must be non-empty")
        if not self.reaction_id.strip():
            raise ValueError("reaction_id must be non-empty")
