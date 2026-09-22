"""t02 — U-MARK reaction catalog + knobs edges (offline)."""

from __future__ import annotations

import pytest

from core.domain.errors import (
    MaxReactionsExceededError,
    ReactionDisabledError,
    ReactionLayerError,
    ReactionMarkError,
    ReactionMutexError,
    UnknownReactionIdError,
)
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_catalog import CATALOG_REACTION_IDS, REACTION_LAYER
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore

_EMOTIONAL = next(rid for rid, layer in REACTION_LAYER.items() if layer == "emotional")
_EPISTEMIC = next(
    rid
    for rid, layer in REACTION_LAYER.items()
    if layer == "epistemic" and rid not in {"agree", "disagree"}
)
_MODERATION = next(rid for rid, layer in REACTION_LAYER.items() if layer == "moderation")


def _key() -> ThreadKey:
    return ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


def _root() -> ReactionTarget:
    return ReactionTarget(kind="thread_root", thread_key=_key())


def _comment(comment_id: str = "c1") -> ReactionTarget:
    return ReactionTarget(kind="comment", thread_key=_key(), comment_id=comment_id)


def _store(*, max_reactions: int = 8) -> InMemoryReactionMarksStore:
    return InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(max_depth=4, max_reactions_per_actor=max_reactions)
    )


def test_u_mark_unknown_id() -> None:
    """U-MARK-unknown-id"""
    store = _store()
    with pytest.raises(UnknownReactionIdError) as exc:
        store.add_mark(ReactionMark(actor_id="a1", target=_root(), reaction_id="not_in_v1"))
    assert isinstance(exc.value, ReactionMarkError)
    assert store.list_marks(_root()) == []


def test_u_mark_disabled() -> None:
    """U-MARK-disabled"""
    store = InMemoryReactionMarksStore(
        knobs=FixedThreadKnobs(
            max_depth=4,
            max_reactions_per_actor=3,
            reactions_enable={_EMOTIONAL: True, "amused": False},
        )
    )
    store.add_mark(ReactionMark(actor_id="a1", target=_root(), reaction_id=_EMOTIONAL))
    with pytest.raises(ReactionDisabledError) as exc:
        store.add_mark(ReactionMark(actor_id="a1", target=_root(), reaction_id="amused"))
    assert isinstance(exc.value, ReactionMarkError)


def test_u_mark_agree_disagree_mutex() -> None:
    """U-MARK-agree-disagree-mutex"""
    store = _store(max_reactions=3)
    target = _comment()
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="agree"))
    with pytest.raises(ReactionMutexError) as exc:
        store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="disagree"))
    assert isinstance(exc.value, ReactionMarkError)
    assert [item.reaction_id for item in store.list_marks(target)] == ["agree"]


def test_u_mark_moderation_on_root() -> None:
    """U-MARK-moderation-on-root"""
    store = _store()
    with pytest.raises(ReactionLayerError) as exc:
        store.add_mark(ReactionMark(actor_id="a1", target=_root(), reaction_id=_MODERATION))
    assert isinstance(exc.value, ReactionMarkError)
    ok = store.add_mark(
        ReactionMark(actor_id="a1", target=_comment(), reaction_id=_MODERATION)
    )
    assert ok.reaction_id == _MODERATION


def test_u_mark_max_reactions_zero_rejected_by_knobs() -> None:
    """U-MARK-max-reactions-0 — domain floor is max_reactions_per_actor >= 1."""
    with pytest.raises(ValueError, match="max_reactions_per_actor"):
        FixedThreadKnobs(max_depth=4, max_reactions_per_actor=0)


def test_u_mark_max_reactions_one() -> None:
    """U-MARK-max-reactions-1"""
    store = _store(max_reactions=1)
    target = _root()
    store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id=_EMOTIONAL))
    with pytest.raises(MaxReactionsExceededError) as exc:
        store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id=_EPISTEMIC))
    assert isinstance(exc.value, ReactionMarkError)
    assert len(store.list_marks(target)) == 1


def test_u_mark_max_reactions_n() -> None:
    """U-MARK-max-reactions-n"""
    store = _store(max_reactions=3)
    target = _root()
    ids = ("acknowledge", "support", "empathy")
    for reaction_id in ids:
        store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id=reaction_id))
    with pytest.raises(MaxReactionsExceededError):
        store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id="concern"))
    assert {item.reaction_id for item in store.list_marks(target)} == set(ids)


@pytest.mark.parametrize(
    ("kind", "comment_id", "reaction_id", "scenario_id"),
    [
        ("thread_root", None, _EMOTIONAL, "U-MARK-emotional-on-root"),
        ("comment", "c-em", _EMOTIONAL, "U-MARK-emotional-on-comment"),
        ("thread_root", None, _EPISTEMIC, "U-MARK-epistemic-on-root"),
        ("comment", "c-ep", _EPISTEMIC, "U-MARK-epistemic-on-comment"),
    ],
)
def test_u_mark_layer_on_root_and_comment(
    kind: str,
    comment_id: str | None,
    reaction_id: str,
    scenario_id: str,
) -> None:
    store = _store()
    target = ReactionTarget(kind=kind, thread_key=_key(), comment_id=comment_id)  # type: ignore[arg-type]
    mark = store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id=reaction_id))
    assert mark.reaction_id == reaction_id
    assert scenario_id.startswith("U-MARK-")


@pytest.mark.parametrize("reaction_id", sorted(CATALOG_REACTION_IDS))
def test_u_mark_catalog_smoke_all_enabled(reaction_id: str) -> None:
    """U-MARK-catalog-smoke-enabled — empty reactions_enable allows all reactions.v1."""
    store = _store(max_reactions=1)
    target = _comment(comment_id=f"c-{reaction_id}")
    mark = store.add_mark(ReactionMark(actor_id="a1", target=target, reaction_id=reaction_id))
    assert mark.reaction_id == reaction_id
    assert store.knobs.reactions_enable == {}
