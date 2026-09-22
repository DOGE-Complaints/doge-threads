"""t03 — E-DOM-DENY unverified or missing opaque; no persist."""

from __future__ import annotations

import pytest

from core.domain.errors import WriteDeniedError
from core.domain.thread_key import ThreadKey
from tc07_e2e_fixtures import cleanup_tc07_prefix, make_e2e_factory, skip_unless_e2e_env, tc07_entity_id
from tc07_traceability import TC07_SCENARIO_IDS


@pytest.mark.domain_e2e
def test_e_dom_deny_missing_opaque_no_persist() -> None:
    assert "E-DOM-DENY-unverified-or-missing-opaque" in TC07_SCENARIO_IDS
    skip_unless_e2e_env()
    factory, values = make_e2e_factory()
    orch = factory.write_orchestrator
    entity_id = tc07_entity_id()
    key = ThreadKey(node="tc07", entity_type="Issue", entity_id=entity_id)
    issue_id = values["THREADS_E2E_ISSUE_ID"]
    db = factory.supabase_db
    assert db is not None
    try:
        with pytest.raises(WriteDeniedError):
            orch.write_comment("", issue_id, key, "tc07 deny must not persist")
        assert factory.discussion_store.list_comments(key) == []
    finally:
        cleanup_tc07_prefix(db, entity_id)
