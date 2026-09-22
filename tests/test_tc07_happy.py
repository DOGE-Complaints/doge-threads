"""t02 — E-DOM-HAPPY three writes against live issue id fixture."""

from __future__ import annotations

from uuid import uuid4

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from tc07_e2e_fixtures import cleanup_tc07_prefix, make_e2e_factory, skip_unless_e2e_env, tc07_entity_id
from tc07_traceability import TC07_SCENARIO_IDS


@pytest.mark.domain_e2e
def test_e_dom_happy_three_writes() -> None:
    assert "E-DOM-HAPPY-comment" in TC07_SCENARIO_IDS
    assert "E-DOM-HAPPY-reaction" in TC07_SCENARIO_IDS
    assert "E-DOM-HAPPY-attachment_ref" in TC07_SCENARIO_IDS
    skip_unless_e2e_env()
    factory, values = make_e2e_factory()
    orch = factory.write_orchestrator
    entity_id = tc07_entity_id()
    key = ThreadKey(node="tc07", entity_type="Issue", entity_id=entity_id)
    issue_id = values["THREADS_E2E_ISSUE_ID"]
    bearer = values["THREADS_E2E_USER_BEARER"]
    db = factory.supabase_db
    assert db is not None
    try:
        comment = orch.write_comment(bearer, issue_id, key, "tc07 domain e2e comment")
        mark = orch.write_reaction(
            bearer,
            issue_id,
            ReactionMark(
                actor_id="tc07-actor",
                target=ReactionTarget(kind="thread_root", thread_key=key),
                reaction_id="acknowledge",
            ),
        )
        ref = orch.write_attachment_ref(
            bearer,
            issue_id,
            AttachmentRef(
                ref_id=uuid4().hex,
                media_type="image/png",
                comment_id=comment.comment_id,
            ),
        )
        listed = factory.discussion_store.list_comments(key)
        assert any(item.comment_id == comment.comment_id for item in listed)
        assert mark.reaction_id == "acknowledge"
        assert ref.comment_id == comment.comment_id
    finally:
        cleanup_tc07_prefix(db, entity_id)
