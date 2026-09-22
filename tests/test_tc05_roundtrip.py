"""t03 — L-PG-RT attach/comment/mark/ref + second client re-read."""

from __future__ import annotations

from uuid import uuid4

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from core.infrastructure.db_supabase import SupabaseDatabase
from tc05_live_fixtures import (
    cleanup_tc05_prefix,
    live_db,
    live_secret_pair,
    live_stores,
    skip_unless_live_secrets,
    tc05_entity_id,
)
from tc05_traceability import TC05_SCENARIO_IDS


@pytest.mark.live_integration
def test_l_pg_rt_crud_two_clients() -> None:
    assert "L-PG-RT-attach" in TC05_SCENARIO_IDS
    assert "L-PG-RT-comment" in TC05_SCENARIO_IDS
    assert "L-PG-RT-mark" in TC05_SCENARIO_IDS
    assert "L-PG-RT-ref" in TC05_SCENARIO_IDS
    assert "L-PG-RT-second-client" in TC05_SCENARIO_IDS
    skip_unless_live_secrets()
    entity_id = tc05_entity_id()
    assert entity_id.startswith("tc05-")
    writer_db = live_db()
    discussion, marks, refs = live_stores(writer_db)
    key = ThreadKey(node="tc05", entity_type="Issue", entity_id=entity_id)
    try:
        attached = discussion.attach_thread(key)
        assert attached.key == key
        comment = discussion.create_comment(key, "tc05 live comment")
        target = ReactionTarget(kind="thread_root", thread_key=key)
        mark = marks.add_mark(
            ReactionMark(actor_id="tc05-actor", target=target, reaction_id="acknowledge")
        )
        ref = refs.accept_ref(
            AttachmentRef(
                ref_id=uuid4().hex,
                media_type="image/png",
                comment_id=comment.comment_id,
            )
        )

        url, role = live_secret_pair()
        reader_db = SupabaseDatabase.from_http(supabase_url=url, service_role_key=role)
        r_disc, r_marks, r_refs = live_stores(reader_db)
        assert r_disc.get_thread(key) is not None
        listed = r_disc.list_comments(key)
        assert any(item.comment_id == comment.comment_id for item in listed)
        assert any(item.reaction_id == mark.reaction_id for item in r_marks.list_marks(target))
        assert any(item.ref_id == ref.ref_id for item in r_refs.list_refs(comment.comment_id))
    finally:
        cleanup_tc05_prefix(writer_db, entity_id)
