from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from core.domain.attachment_ref import AttachmentRef
from core.domain.comment import Comment
from core.domain.reaction_mark import ReactionMark, ReactionTarget
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


class ReactionMarksStore(Protocol):
    """Store catalog reaction marks. No ranking / voice-weight application."""

    def add_mark(self, mark: ReactionMark) -> ReactionMark:
        """Persist a mark or reject per catalog / knobs rules."""
        ...

    def remove_mark(self, mark: ReactionMark) -> None:
        """Drop actor × target × reaction_id if present (idempotent)."""
        ...

    def list_marks(self, target: ReactionTarget) -> list[ReactionMark]:
        """Return marks for a target in insertion order."""
        ...


class MediaFloor(Protocol):
    """Platform legal media floor. Node knobs cannot disable this hook."""

    def honour(self, ref: AttachmentRef) -> None:
        """Reject CSAM / catastrophic before a ref is stored. Not a scanner vendor."""
        ...


class AttachmentRefStore(Protocol):
    """Persist attachment references only. No byte store."""

    def accept_ref(self, ref: AttachmentRef) -> AttachmentRef:
        """Honour floor, then allowlist, then persist the reference."""
        ...

    def list_refs(self, comment_id: str) -> list[AttachmentRef]:
        """Return refs for a comment in insertion order."""
        ...


class ThreadWritePort(Protocol):
    """Arch §3 write kinds. Domain/application API only — no public HTTP."""

    def write_comment(
        self,
        bearer_token: str,
        issue_id: str,
        key: ThreadKey,
        body: str,
        *,
        parent_id: str | None = None,
    ) -> Comment:
        """Compose-pull → verify → depth enforce → persist comment."""
        ...

    def write_reaction(
        self,
        bearer_token: str,
        issue_id: str,
        mark: ReactionMark,
    ) -> ReactionMark:
        """Compose-pull → verify → enable/max → persist mark."""
        ...

    def remove_reaction(
        self,
        bearer_token: str,
        issue_id: str,
        mark: ReactionMark,
    ) -> None:
        """Compose-pull → verify → drop mark (FE op=remove)."""
        ...

    def list_reaction_marks(self, target: ReactionTarget) -> list[ReactionMark]:
        """Return marks for a target (U2 aggregates)."""
        ...

    def write_attachment_ref(
        self,
        bearer_token: str,
        issue_id: str,
        ref: AttachmentRef,
    ) -> AttachmentRef:
        """Compose-pull → verify → allowlist+floor → persist ref."""
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
