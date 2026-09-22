"""t02 — L-OR-WR three writes; L-OR-RR new client reads."""

from __future__ import annotations

from uuid import uuid4

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from tc06_live_fixtures import (
    cleanup_tc06_prefix,
    make_live_orch_harness,
    new_reader_stores,
    patch_gateway,
    skip_unless_live_secrets,
    tc06_entity_id,
)
from tc06_traceability import TC06_SCENARIO_IDS
from threadcontext_fixtures import SAMPLE_ISSUE_ID


@pytest.mark.live_integration
def test_l_or_wr_rr_three_writes_new_client() -> None:
    assert "L-OR-WR-comment" in TC06_SCENARIO_IDS
    assert "L-OR-WR-reaction" in TC06_SCENARIO_IDS
    assert "L-OR-WR-attachment_ref" in TC06_SCENARIO_IDS
    assert "L-OR-RR-comment" in TC06_SCENARIO_IDS
    assert "L-OR-RR-reaction" in TC06_SCENARIO_IDS
    assert "L-OR-RR-attachment_ref" in TC06_SCENARIO_IDS
    skip_unless_live_secrets()
    entity_id = tc06_entity_id()
    harness = make_live_orch_harness()
    key = ThreadKey(node="tc06", entity_type="Issue", entity_id=entity_id)
    try:
        with patch_gateway(harness.mock_http):
            comment = harness.orchestrator.write_comment(
                "tok", SAMPLE_ISSUE_ID, key, "tc06 live orch comment"
            )
            mark = harness.orchestrator.write_reaction(
                "tok",
                SAMPLE_ISSUE_ID,
                ReactionMark(
                    actor_id="tc06-actor",
                    target=ReactionTarget(kind="thread_root", thread_key=key),
                    reaction_id="acknowledge",
                ),
            )
            ref = harness.orchestrator.write_attachment_ref(
                "tok",
                SAMPLE_ISSUE_ID,
                AttachmentRef(
                    ref_id=uuid4().hex,
                    media_type="image/png",
                    comment_id=comment.comment_id,
                ),
            )
        harness.me.fetch_me.assert_called()
        r_disc, r_marks, r_refs, _reader_db = new_reader_stores()
        listed = r_disc.list_comments(key)
        assert any(item.comment_id == comment.comment_id for item in listed)
        target = ReactionTarget(kind="thread_root", thread_key=key)
        assert any(item.reaction_id == mark.reaction_id for item in r_marks.list_marks(target))
        assert any(item.ref_id == ref.ref_id for item in r_refs.list_refs(comment.comment_id))
    finally:
        cleanup_tc06_prefix(harness.db, entity_id)
