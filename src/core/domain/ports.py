from __future__ import annotations

from typing import Protocol

from core.domain.comment import Comment
from core.domain.thread_key import Thread, ThreadKey


class ThreadKnobs(Protocol):
    """Injected depth knobs. Values arrive later via 01-02 compose-pull."""

    @property
    def max_depth(self) -> int:
        """Maximum allowed comment depth (root = 1)."""
        ...


class ThreadKeyPort(Protocol):
    """Attach/get a Thread by (node, entity_type, entity_id). No Issue ownership."""

    def attach_thread(self, key: ThreadKey) -> Thread:
        """Attach or return the thread for an external entity key."""
        ...

    def get_thread(self, key: ThreadKey) -> Thread | None:
        """Return the attached thread or None."""
        ...


class DiscussionStore(ThreadKeyPort, Protocol):
    """In-process discussion store: thread key + nested comment tree."""

    def create_comment(
        self,
        key: ThreadKey,
        body: str,
        *,
        parent_id: str | None = None,
    ) -> Comment:
        """Create a comment. Must not mutate Story or cluster."""
        ...

    def list_comments(self, key: ThreadKey) -> list[Comment]:
        """Return comments for the thread in insertion order."""
        ...
