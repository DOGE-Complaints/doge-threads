"""t04 — L-PG-UQ live unique mark; L-PG-RLS service_role write."""

from __future__ import annotations

import pytest
import httpx

from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from core.infrastructure.supabase_marks_mappers import mark_to_row
from tc05_live_fixtures import cleanup_tc05_prefix, live_db, live_stores, skip_unless_live_secrets, tc05_entity_id
from tc05_traceability import TC05_SCENARIO_IDS


@pytest.mark.live_integration
def test_l_pg_uq_dup_mark_and_rls_service_role() -> None:
    assert "L-PG-UQ-dup-mark" in TC05_SCENARIO_IDS
    assert "L-PG-RLS-service-role-write" in TC05_SCENARIO_IDS
    skip_unless_live_secrets()
    entity_id = tc05_entity_id()
    db = live_db()
    discussion, marks, _refs = live_stores(db)
    key = ThreadKey(node="tc05", entity_type="Issue", entity_id=entity_id)
    try:
        discussion.attach_thread(key)
        target = ReactionTarget(kind="thread_root", thread_key=key)
        mark = ReactionMark(actor_id="tc05-uq", target=target, reaction_id="acknowledge")
        written = marks.add_mark(mark)
        assert written.reaction_id == "acknowledge"
        # L-PG-RLS: service_role POST succeeded under RLS (would be 401/403 if denied).
        row = mark_to_row(mark)
        with pytest.raises(httpx.HTTPStatusError) as exc:
            db._request(
                method="POST",
                path="/rest/v1/thread_reaction_marks",
                json_body=row,
                prefer="return=representation",
            )
        assert exc.value.response.status_code == 409
    finally:
        cleanup_tc05_prefix(db, entity_id)
