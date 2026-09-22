from __future__ import annotations

from core.domain import CIVIC_FIRST_ENTITY_TYPE, Thread, ThreadKey
from core.domain.ports import ThreadKeyPort
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.domain.knobs import FixedThreadKnobs


def test_thread_key_fields() -> None:
    key = ThreadKey(node="node-a", entity_type=CIVIC_FIRST_ENTITY_TYPE, entity_id="issue-1")
    assert key.node == "node-a"
    assert key.entity_type == "Issue"
    assert key.entity_id == "issue-1"


def test_civic_first_type_is_logical_issue() -> None:
    assert CIVIC_FIRST_ENTITY_TYPE == "Issue"


def test_attach_thread_by_external_key() -> None:
    store: ThreadKeyPort = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=3))
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    thread = store.attach_thread(key)
    assert isinstance(thread, Thread)
    assert thread.key == key
    assert store.get_thread(key) is thread


def test_attach_is_idempotent() -> None:
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=3))
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    first = store.attach_thread(key)
    second = store.attach_thread(key)
    assert first is second
