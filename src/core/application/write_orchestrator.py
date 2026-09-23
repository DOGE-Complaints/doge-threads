from __future__ import annotations

from core.application.pull_thread_context import pull_and_compose
from core.application.write_gate import assert_write_allowed
from core.domain.attachment_ref import AttachmentRef
from core.domain.comment import Comment
from core.domain.errors import ThreadContextError
from core.domain.ports import (
    AttachmentRefStore,
    DiscussionStore,
    ReactionMarksStore,
    WriteGate,
)
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_context import ThreadContext
from core.domain.thread_key import ThreadKey
from core.gateway.client import GatewayClient


class ThreadWriteOrchestrator:
    """Arch §3 write path: compose-pull → verify → enforce → persist. No HTTP."""

    def __init__(
        self,
        *,
        gateway: GatewayClient | None,
        write_gate: WriteGate,
        discussion_store: DiscussionStore,
        reaction_store: ReactionMarksStore,
        attachment_store: AttachmentRefStore,
    ) -> None:
        self._gateway = gateway
        self._gate = write_gate
        self._discussion = discussion_store
        self._reactions = reaction_store
        self._attachments = attachment_store

    def _compose(self, issue_id: str) -> ThreadContext:
        if self._gateway is None:
            raise ThreadContextError("gateway client unavailable")
        return pull_and_compose(self._gateway, issue_id)

    def write_comment(
        self,
        bearer_token: str,
        issue_id: str,
        key: ThreadKey,
        body: str,
        *,
        parent_id: str | None = None,
    ) -> Comment:
        """Compose-pull → identity_verified → depth persist."""
        self._compose(issue_id)
        assert_write_allowed(self._gate, bearer_token)
        self._discussion.attach_thread(key)
        return self._discussion.create_comment(key, body, parent_id=parent_id)

    def write_reaction(
        self,
        bearer_token: str,
        issue_id: str,
        mark: ReactionMark,
    ) -> ReactionMark:
        """Compose-pull → identity_verified → enable/max persist marks."""
        self._compose(issue_id)
        assert_write_allowed(self._gate, bearer_token)
        return self._reactions.add_mark(mark)

    def remove_reaction(
        self,
        bearer_token: str,
        issue_id: str,
        mark: ReactionMark,
    ) -> None:
        """Compose-pull → identity_verified → drop mark (idempotent)."""
        self._compose(issue_id)
        assert_write_allowed(self._gate, bearer_token)
        self._reactions.remove_mark(mark)

    def list_reaction_marks(self, target: ReactionTarget) -> list[ReactionMark]:
        """Read marks for a target after a write (U2 aggregates)."""
        return self._reactions.list_marks(target)

    def write_attachment_ref(
        self,
        bearer_token: str,
        issue_id: str,
        ref: AttachmentRef,
    ) -> AttachmentRef:
        """Compose-pull → identity_verified → allowlist+floor persist refs."""
        self._compose(issue_id)
        assert_write_allowed(self._gate, bearer_token)
        return self._attachments.accept_ref(ref)
