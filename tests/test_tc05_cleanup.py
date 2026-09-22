"""t05 — L-PG-CLN tc05-{uuid} isolation + optional delete."""

from __future__ import annotations

import pytest

from core.domain.thread_key import ThreadKey
from tc05_live_fixtures import cleanup_tc05_prefix, live_db, live_stores, skip_unless_live_secrets, tc05_entity_id
from tc05_traceability import TC05_SCENARIO_IDS


@pytest.mark.live_integration
def test_l_pg_cln_prefix_and_optional_delete() -> None:
    assert "L-PG-CLN-prefix" in TC05_SCENARIO_IDS
    assert "L-PG-CLN-optional-delete" in TC05_SCENARIO_IDS
    skip_unless_live_secrets()
    entity_id = tc05_entity_id()
    assert entity_id.startswith("tc05-")
    db = live_db()
    discussion, _marks, _refs = live_stores(db)
    key = ThreadKey(node="tc05", entity_type="Issue", entity_id=entity_id)
    discussion.attach_thread(key)
    assert discussion.get_thread(key) is not None
    cleanup_tc05_prefix(db, entity_id)
    assert discussion.get_thread(key) is None
