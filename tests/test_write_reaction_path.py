from __future__ import annotations

import pytest

from core.domain import ThreadKey, WriteDeniedError
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from threadcontext_fixtures import SAMPLE_ISSUE_ID
from write_orchestrator_fixtures import make_orchestrator, patch_gateway


def _mark() -> ReactionMark:
    return ReactionMark(
        actor_id="a1",
        target=ReactionTarget(
            kind="thread_root",
            thread_key=ThreadKey(node="n1", entity_type="Issue", entity_id="e1"),
        ),
        reaction_id="acknowledge",
    )


def test_reaction_write_same_verify_then_marks() -> None:
    orch, _store, marks, _refs, mock_http, me = make_orchestrator(verified=True)
    mark = _mark()
    with patch_gateway(mock_http):
        stored = orch.write_reaction("tok", SAMPLE_ISSUE_ID, mark)
    assert stored == mark
    assert marks.list_marks(mark.target) == [mark]
    me.fetch_me.assert_called_once_with("tok")


def test_reaction_write_denied() -> None:
    orch, _store, marks, _refs, mock_http, _me = make_orchestrator(verified=False)
    mark = _mark()
    with patch_gateway(mock_http), pytest.raises(WriteDeniedError):
        orch.write_reaction("tok", SAMPLE_ISSUE_ID, mark)
    assert marks.list_marks(mark.target) == []
