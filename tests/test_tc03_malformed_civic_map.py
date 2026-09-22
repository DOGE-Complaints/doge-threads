"""t04/t05 — C-PG-BAD-* malformed/civic; C-PG-MAP-* 01-08 write columns."""

from __future__ import annotations

import pytest

from core.domain.attachment_ref import AttachmentRef
from core.domain.comment import Comment
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import Thread, ThreadKey
from core.infrastructure.supabase_discussion_mappers import (
    COMMENT_WRITE_COLUMNS,
    THREAD_WRITE_COLUMNS,
    comment_from_row,
    comment_to_row,
    thread_from_row,
    thread_to_row,
)
from core.infrastructure.supabase_discussion_store import _as_rows
from core.infrastructure.supabase_marks_mappers import MARK_WRITE_COLUMNS, mark_from_row, mark_to_row
from core.infrastructure.supabase_refs_mappers import REF_WRITE_COLUMNS, ref_from_row, ref_to_row
from tc03_fake_postgrest import (
    CIVIC_PATH_TOKENS,
    DDL_COMMENT_COLUMNS,
    DDL_MARK_COLUMNS,
    DDL_REF_COLUMNS,
    DDL_THREAD_COLUMNS,
    FakeContractPostgrest,
    discussion_store,
)
from tc03_traceability import TC03_SCENARIO_IDS

_KEY = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


def test_c_pg_bad_non_list_and_malformed_row() -> None:
    assert "C-PG-BAD-non-list" in TC03_SCENARIO_IDS
    assert "C-PG-BAD-malformed-row" in TC03_SCENARIO_IDS
    assert _as_rows("not-a-list") == []
    assert _as_rows(42) == []
    assert _as_rows(["x", 1]) == []
    with pytest.raises(KeyError):
        mark_from_row({"actor_id": "a1"})
    with pytest.raises((KeyError, ValueError, TypeError)):
        comment_from_row({"comment_id": "c1"})


def test_c_pg_bad_civic_path_assertion() -> None:
    assert "C-PG-BAD-civic-stories" in TC03_SCENARIO_IDS
    assert "C-PG-BAD-civic-issues" in TC03_SCENARIO_IDS
    fake = FakeContractPostgrest()
    with pytest.raises(AssertionError, match="civic path forbidden"):
        fake._request(method="GET", path="/rest/v1/stories")
    with pytest.raises(AssertionError, match="civic path forbidden"):
        fake._request(method="GET", path="/rest/v1/issues")
    store, wired = discussion_store()
    store.attach_thread(_KEY)
    store.create_comment(_KEY, "hello")
    assert all(not any(token in path for token in CIVIC_PATH_TOKENS) for _, path in wired.calls)


def test_c_pg_map_write_columns_subset_of_01_08() -> None:
    assert "C-PG-MAP-thread" in TC03_SCENARIO_IDS
    assert "C-PG-MAP-comment" in TC03_SCENARIO_IDS
    assert "C-PG-MAP-mark" in TC03_SCENARIO_IDS
    assert "C-PG-MAP-ref" in TC03_SCENARIO_IDS
    thread_row = thread_to_row(Thread(key=_KEY))
    assert set(thread_row) == THREAD_WRITE_COLUMNS
    assert THREAD_WRITE_COLUMNS <= DDL_THREAD_COLUMNS
    assert "created_at" not in thread_row
    assert thread_from_row({**thread_row, "created_at": "now"}).key == _KEY

    comment = Comment(comment_id="c1", thread_key=_KEY, parent_id=None, body="x", depth=1)
    comment_row = comment_to_row(comment)
    assert set(comment_row) == COMMENT_WRITE_COLUMNS
    assert COMMENT_WRITE_COLUMNS <= DDL_COMMENT_COLUMNS
    assert "created_at" not in comment_row

    mark = ReactionMark(
        actor_id="a1",
        target=ReactionTarget(kind="thread_root", thread_key=_KEY),
        reaction_id="acknowledge",
    )
    mark_row = mark_to_row(mark)
    assert set(mark_row) == MARK_WRITE_COLUMNS
    assert MARK_WRITE_COLUMNS <= DDL_MARK_COLUMNS
    assert "created_at" not in mark_row
    assert mark_from_row({**mark_row, "created_at": "now"}).reaction_id == "acknowledge"

    ref = AttachmentRef(ref_id="r1", media_type="image/png", comment_id="c1")
    ref_row = ref_to_row(ref)
    assert set(ref_row) == REF_WRITE_COLUMNS
    assert REF_WRITE_COLUMNS <= DDL_REF_COLUMNS
    assert "created_at" not in ref_row
    assert ref_from_row({**ref_row, "created_at": "now"}).ref_id == "r1"
