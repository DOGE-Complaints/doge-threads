from __future__ import annotations

import pytest

from core.domain import ReactionLayerError, ThreadKey
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore


def _store() -> InMemoryReactionMarksStore:
    return InMemoryReactionMarksStore(knobs=FixedThreadKnobs(max_depth=4, max_reactions_per_actor=3))


def _key() -> ThreadKey:
    return ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


def test_emotional_and_epistemic_on_root_and_comment() -> None:
    store = _store()
    key = _key()
    root = ReactionTarget(kind="thread_root", thread_key=key)
    comment = ReactionTarget(kind="comment", thread_key=key, comment_id="c1")
    store.add_mark(ReactionMark(actor_id="a1", target=root, reaction_id="support"))
    store.add_mark(ReactionMark(actor_id="a1", target=root, reaction_id="agree"))
    store.add_mark(ReactionMark(actor_id="a1", target=comment, reaction_id="empathy"))
    store.add_mark(ReactionMark(actor_id="a1", target=comment, reaction_id="useful_fact"))
    assert {item.reaction_id for item in store.list_marks(root)} == {"support", "agree"}
    assert {item.reaction_id for item in store.list_marks(comment)} == {"empathy", "useful_fact"}


def test_moderation_comments_only() -> None:
    store = _store()
    key = _key()
    root = ReactionTarget(kind="thread_root", thread_key=key)
    comment = ReactionTarget(kind="comment", thread_key=key, comment_id="c1")
    with pytest.raises(ReactionLayerError):
        store.add_mark(ReactionMark(actor_id="a1", target=root, reaction_id="off_topic"))
    stored = store.add_mark(ReactionMark(actor_id="a1", target=comment, reaction_id="aggressive"))
    assert stored.reaction_id == "aggressive"
