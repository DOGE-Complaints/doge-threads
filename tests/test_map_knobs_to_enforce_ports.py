from __future__ import annotations

from core.application.map_shell_knobs import map_pack_shell_settings_to_knobs
from core.domain import DepthExceededError, ThreadKey
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from threadcontext_fixtures import SAMPLE_SETTINGS_PAYLOAD

import pytest


def test_map_settings_into_fixed_thread_knobs() -> None:
    knobs = map_pack_shell_settings_to_knobs(SAMPLE_SETTINGS_PAYLOAD)
    assert knobs.max_depth == 3
    assert knobs.max_reactions_per_actor == 2
    assert knobs.reactions_enable == {"like": True}
    assert knobs.media_allowed_types == ("image/png",)


def test_mapped_knobs_enforce_store_depth() -> None:
    knobs = map_pack_shell_settings_to_knobs(SAMPLE_SETTINGS_PAYLOAD)
    store = InMemoryDiscussionStore(knobs=knobs)
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    store.attach_thread(key)
    root = store.create_comment(key, "d1")
    child = store.create_comment(key, "d2", parent_id=root.comment_id)
    grandchild = store.create_comment(key, "d3", parent_id=child.comment_id)
    assert grandchild.depth == 3
    with pytest.raises(DepthExceededError) as exc:
        store.create_comment(key, "d4", parent_id=grandchild.comment_id)
    assert exc.value.max_depth == 3
    assert store.knobs.max_reactions_per_actor == 2
    assert store.knobs.media_allowed_types == ("image/png",)
