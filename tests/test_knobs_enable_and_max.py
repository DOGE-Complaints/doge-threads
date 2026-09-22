from __future__ import annotations

import pytest

from core.domain import MaxReactionsExceededError, ReactionDisabledError, ThreadKey
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore


def _target() -> ReactionTarget:
    return ReactionTarget(
        kind="thread_root",
        thread_key=ThreadKey(node="n1", entity_type="Issue", entity_id="e1"),
    )


def test_disabled_reaction_id_rejected() -> None:
    store = InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(
            max_depth=4,
            max_reactions_per_actor=3,
            reactions_enable={"acknowledge": True, "amused": False},
        )
    )
    target = _target()
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="acknowledge"))
    with pytest.raises(ReactionDisabledError):
        store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="amused"))


def test_max_reactions_per_actor_enforced() -> None:
    store = InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(max_depth=4, max_reactions_per_actor=2)
    )
    target = _target()
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="acknowledge"))
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="support"))
    with pytest.raises(MaxReactionsExceededError):
        store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="empathy"))
    assert len(store.list_marks(target)) == 2
