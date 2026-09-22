from __future__ import annotations

import pytest

from core.domain import ThreadKey, UnknownReactionIdError
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_catalog import CATALOG_REACTION_IDS
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore


def _store() -> InMemoryReactionMarksStore:
    return InMemoryReactionMarksStore(knobs=FixedThreadKnobs(max_depth=4, max_reactions_per_actor=3))


def _root() -> ReactionTarget:
    return ReactionTarget(
        kind="thread_root",
        thread_key=ThreadKey(node="n1", entity_type="Issue", entity_id="e1"),
    )


def test_store_catalog_reaction_id_without_rename() -> None:
    store = _store()
    mark = ReactionMark(actor_id="a1", target=_root(), reaction_id="acknowledge")
    stored = store.add_mark(mark)
    assert stored.reaction_id == "acknowledge"
    assert stored.reaction_id in CATALOG_REACTION_IDS
    assert store.list_marks(_root()) == [stored]


def test_unknown_reaction_id_rejected() -> None:
    store = _store()
    with pytest.raises(UnknownReactionIdError):
        store.add_mark(ReactionMark(actor_id="a1", target=_root(), reaction_id="like"))
