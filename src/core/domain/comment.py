from __future__ import annotations

from dataclasses import dataclass

from core.domain.thread_key import ThreadKey


@dataclass(frozen=True)
class Comment:
    """Nested tree node. Not a Story; create does not mutate clustering."""

    comment_id: str
    thread_key: ThreadKey
    parent_id: str | None
    body: str
    depth: int
