from __future__ import annotations

from unittest.mock import MagicMock, patch

from core.application.write_gate import IdentityVerifiedWriteGate
from core.application.write_orchestrator import ThreadWriteOrchestrator
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from threadcontext_fixtures import stub_gateway_client


def make_orchestrator(*, verified: bool = True) -> tuple[
    ThreadWriteOrchestrator,
    InMemoryDiscussionStore,
    InMemoryReactionMarksStore,
    InMemoryAttachmentRefStore,
    MagicMock,
    MagicMock,
]:
    knobs = FixedThreadKnobs(
        max_depth=3,
        max_reactions_per_actor=3,
        media_allowed_types=("image/png",),
    )
    discussion = InMemoryDiscussionStore(knobs=knobs)
    reactions = InMemoryReactionMarksStore(knobs=knobs)
    attachments = InMemoryAttachmentRefStore(knobs=knobs)
    me = MagicMock()
    me.fetch_me.return_value = {"data": {"identity_verified": verified}}
    gateway, mock_http = stub_gateway_client()
    orchestrator = ThreadWriteOrchestrator(
        gateway=gateway,
        write_gate=IdentityVerifiedWriteGate(me),
        discussion_store=discussion,
        reaction_store=reactions,
        attachment_store=attachments,
    )
    return orchestrator, discussion, reactions, attachments, mock_http, me


def patch_gateway(mock_http: MagicMock):
    return patch("core.gateway.client.httpx.Client", return_value=mock_http)
