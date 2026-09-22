"""t02 — L-PG-RDY / L-PG-SCH live readiness + schema smoke."""

from __future__ import annotations

import pytest

from core.infrastructure.db_supabase import REQUIRED_READINESS_TABLES
from tc05_live_fixtures import live_db
from tc05_traceability import TC05_SCENARIO_IDS


@pytest.mark.live_integration
def test_l_pg_rdy_tables_ready() -> None:
    assert "L-PG-RDY-tables-ready" in TC05_SCENARIO_IDS
    db = live_db()
    assert db.required_tables_ready() is True


@pytest.mark.live_integration
@pytest.mark.parametrize(
    ("table", "scenario_id"),
    [
        ("thread_threads", "L-PG-SCH-thread-threads"),
        ("thread_comments", "L-PG-SCH-thread-comments"),
        ("thread_reaction_marks", "L-PG-SCH-thread-reaction-marks"),
        ("thread_attachment_refs", "L-PG-SCH-thread-attachment-refs"),
    ],
)
def test_l_pg_sch_select_four_tables(table: str, scenario_id: str) -> None:
    assert table in REQUIRED_READINESS_TABLES
    assert scenario_id in TC05_SCENARIO_IDS
    db = live_db()
    payload = db._request(
        method="GET",
        path=f"/rest/v1/{table}",
        params={"select": "*", "limit": "1"},
    )
    assert payload is None or isinstance(payload, list)
