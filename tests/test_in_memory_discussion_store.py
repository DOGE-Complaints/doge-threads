from __future__ import annotations

from core.domain import Comment, ThreadKey
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.providers import provide_service_factory


def test_nested_comment_tree() -> None:
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=4))
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    store.attach_thread(key)
    root = store.create_comment(key, "root")
    child = store.create_comment(key, "child", parent_id=root.comment_id)
    assert isinstance(root, Comment)
    assert root.depth == 1
    assert child.depth == 2
    assert child.parent_id == root.comment_id
    assert [item.comment_id for item in store.list_comments(key)] == [
        root.comment_id,
        child.comment_id,
    ]


def test_factory_hooks_in_memory_store(app_config) -> None:
    factory = provide_service_factory(app_config)
    assert factory.discussion_store is not None
    assert isinstance(factory.discussion_store, InMemoryDiscussionStore)
    assert factory.thread_knobs.max_depth == 8
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e9")
    factory.discussion_store.attach_thread(key)
    comment = factory.discussion_store.create_comment(key, "via factory")
    assert comment.body == "via factory"
