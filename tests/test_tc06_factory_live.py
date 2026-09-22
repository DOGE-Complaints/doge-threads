"""t01 — factory supabase + stub Me/GW; knobs fixed."""

from __future__ import annotations

import pytest

from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.supabase_attachment_ref_store import SupabaseAttachmentRefStore
from core.infrastructure.supabase_discussion_store import SupabaseDiscussionStore
from core.infrastructure.supabase_reaction_marks_store import SupabaseReactionMarksStore
from tc05_live_fixtures import skip_unless_live_secrets
from tc06_live_fixtures import make_live_orch_harness


@pytest.mark.live_integration
def test_factory_live_supabase_stub_siblings() -> None:
    skip_unless_live_secrets()
    harness = make_live_orch_harness()
    assert harness.factory.db_backend == "supabase"
    assert isinstance(harness.discussion, SupabaseDiscussionStore)
    assert isinstance(harness.reactions, SupabaseReactionMarksStore)
    assert isinstance(harness.attachments, SupabaseAttachmentRefStore)
    assert isinstance(harness.factory.thread_knobs, FixedThreadKnobs)
    assert harness.factory.thread_knobs.max_depth == 8
    assert harness.me.fetch_me.return_value == {"data": {"identity_verified": True}}
    assert harness.orchestrator._gateway is not None
