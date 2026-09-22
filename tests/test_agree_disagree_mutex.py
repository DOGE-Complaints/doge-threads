from __future__ import annotations

import pytest

from core.domain import ReactionMutexError, ThreadKey
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore


def test_agree_and_disagree_mutex_on_same_target() -> None:
    store = InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(max_depth=4, max_reactions_per_actor=3)
    )
    target = ReactionTarget(
        kind="comment",
        thread_key=ThreadKey(node="n1", entity_type="Issue", entity_id="e1"),
        comment_id="c1",
    )
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="agree"))
    with pytest.raises(ReactionMutexError):
        store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="disagree"))
    assert [item.reaction_id for item in store.list_marks(target)] == ["agree"]


def test_other_actor_may_disagree() -> None:
    store = InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(max_depth=4, max_reactions_per_actor=3)
    )
    target = ReactionTarget(
        kind="comment",
        thread_key=ThreadKey(node="n1", entity_type="Issue", entity_id="e1"),
        comment_id="c1",
    )
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="agree"))
    other = store.add_mark(ReactionMark(actor_id="a2", target=target, reaction_id="disagree"))
    assert other.reaction_id == "disagree"
