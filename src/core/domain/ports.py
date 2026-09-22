from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from core.domain.comment import Comment
from core.domain.thread_context import IssueProjection, ThreadContext
from core.domain.thread_key import Thread, ThreadKey


class ThreadKnobs(Protocol):
    """Injected knobs. Values arrive via 01-02 compose-pull (not a pack loader)."""

    @property
    def max_depth(self) -> int:
        """Maximum allowed comment depth (root = 1)."""
        ...

    @property
    def max_reactions_per_actor(self) -> int:
        """Maximum reaction marks per actor (01-04)."""
        ...

    @property
    def reactions_enable(self) -> Mapping[str, bool]:
        """Reaction type enables from pack_shell_settings.threads.reactions.enable."""
        ...

    @property
    def media_allowed_types(self) -> tuple[str, ...]:
        """Attachment allowlist from pack_shell_settings.threads.media.allowed_types."""
        ...


class ThreadContextPort(Protocol):
    """Compose logical ThreadContext from Issue materials + pack_shell_settings."""

    def compose(
        self,
        issue: IssueProjection,
        settings: Mapping[str, Any],
    ) -> ThreadContext:
        """Compose ThreadContext. No pack loader; no Story narrative."""
        ...


class ThreadKeyPort(Protocol):
    """Attach/get a Thread by (node, entity_type, entity_id). No Issue ownership."""

    def attach_thread(self, key: ThreadKey) -> Thread:
        """Attach or return the thread for an external entity key."""
        ...

    def get_thread(self, key: ThreadKey) -> Thread | None:
        """Return the attached thread or None."""
        ...


class WriteGate(Protocol):
    """Allow a thread write only when identity_verified is True."""

    def allow_write(self, bearer_token: str) -> bool:
        """Return True only for method-opaque identity_verified is True."""
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
