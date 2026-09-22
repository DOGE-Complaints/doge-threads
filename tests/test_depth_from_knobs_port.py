from __future__ import annotations

import inspect

import pytest

from core.domain import DepthExceededError, ThreadKey
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure import providers as providers_mod


def test_depth_over_max_rejected() -> None:
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=2))
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    store.attach_thread(key)
    root = store.create_comment(key, "root")
    child = store.create_comment(key, "child", parent_id=root.comment_id)
    assert child.depth == 2
    with pytest.raises(DepthExceededError) as exc:
        store.create_comment(key, "too-deep", parent_id=child.comment_id)
    assert exc.value.depth == 3
    assert exc.value.max_depth == 2


def test_injected_knobs_not_pack_loader() -> None:
    source = inspect.getsource(providers_mod)
    assert "pack_loader" not in source
    assert "load_pack" not in source
    store_source = inspect.getsource(InMemoryDiscussionStore)
    assert "pack_loader" not in store_source
