"""t01 — U-KEY / U-DISC ThreadKey + in_memory discussion edges (offline)."""

from __future__ import annotations

import pytest

from core.domain.errors import (
    CommentNotFoundError,
    DepthExceededError,
    DiscussionStoreError,
    ThreadNotFoundError,
)
from core.domain.knobs import FixedThreadKnobs
from core.domain.thread_key import ThreadKey
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore


def _store(*, max_depth: int = 3) -> InMemoryDiscussionStore:
    return InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=max_depth))


def _key() -> ThreadKey:
    return ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


@pytest.mark.parametrize(
    ("field", "scenario_id"),
    [
        ("node", "U-KEY-empty-node"),
        ("entity_type", "U-KEY-empty-type"),
        ("entity_id", "U-KEY-empty-id"),
    ],
)
@pytest.mark.parametrize("blank", ("", "   "))
def test_u_key_empty_fields_raise_value_error(
    field: str, scenario_id: str, blank: str
) -> None:
    kwargs = {"node": "n1", "entity_type": "Issue", "entity_id": "e1", field: blank}
    with pytest.raises(ValueError):
        ThreadKey(**kwargs)
    assert scenario_id.startswith("U-KEY-")


def test_u_disc_not_attached_raises_thread_not_found() -> None:
    """U-DISC-not-attached"""
    store = _store()
    key = _key()
    with pytest.raises(ThreadNotFoundError) as exc:
        store.create_comment(key, "orphan")
    assert isinstance(exc.value, DiscussionStoreError)
    assert store.list_comments(key) == []
    assert store.civic_side_effects.story_creates == []


def test_u_disc_bad_parent_raises_comment_not_found() -> None:
    """U-DISC-bad-parent"""
    store = _store()
    key = _key()
    store.attach_thread(key)
    with pytest.raises(CommentNotFoundError) as exc:
        store.create_comment(key, "child", parent_id="missing-parent")
    assert isinstance(exc.value, DiscussionStoreError)
    assert store.list_comments(key) == []
    assert store.civic_side_effects.story_mutations == []


def test_u_disc_depth_eq_max_ok_and_chain() -> None:
    """U-DISC-depth-eq-max-ok U-DISC-nested-chain-to-max U-DISC-civic-side-effects-empty"""
    store = _store(max_depth=3)
    key = _key()
    store.attach_thread(key)
    root = store.create_comment(key, "d1")
    child = store.create_comment(key, "d2", parent_id=root.comment_id)
    leaf = store.create_comment(key, "d3", parent_id=child.comment_id)
    assert (root.depth, child.depth, leaf.depth) == (1, 2, 3)
    assert leaf.depth == store.knobs.max_depth
    effects = store.civic_side_effects
    assert effects.story_creates == []
    assert effects.story_mutations == []
    assert effects.cluster_mutations == []


def test_u_disc_depth_max_plus_one_raises() -> None:
    """U-DISC-depth-max-plus-1"""
    store = _store(max_depth=2)
    key = _key()
    store.attach_thread(key)
    root = store.create_comment(key, "d1")
    child = store.create_comment(key, "d2", parent_id=root.comment_id)
    assert child.depth == 2
    with pytest.raises(DepthExceededError) as exc:
        store.create_comment(key, "d3", parent_id=child.comment_id)
    assert exc.value.max_depth == 2
    assert exc.value.depth == 3
    assert isinstance(exc.value, DiscussionStoreError)
    assert len(store.list_comments(key)) == 2
    assert store.civic_side_effects.cluster_mutations == []
