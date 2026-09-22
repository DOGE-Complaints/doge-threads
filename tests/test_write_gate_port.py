from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.application.write_gate import (
    IdentityVerifiedWriteGate,
    attach_thread_if_allowed,
    create_comment_if_allowed,
)
from core.domain import ThreadKey, WriteDeniedError
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore


def _store() -> InMemoryDiscussionStore:
    return InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=3))


def test_write_gate_allows_only_identity_verified_true() -> None:
    client = MagicMock()
    client.fetch_me.return_value = {"data": {"identity_verified": True}}
    gate = IdentityVerifiedWriteGate(client)
    assert gate.allow_write("tok") is True


def test_create_comment_requires_gate_before_store_write() -> None:
    store = _store()
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    client = MagicMock()
    client.fetch_me.return_value = {"data": {"identity_verified": False}}
    gate = IdentityVerifiedWriteGate(client)
    with pytest.raises(WriteDeniedError):
        create_comment_if_allowed(store, gate, "tok", key, "nope")
    assert store.get_thread(key) is None
    assert store.list_comments(key) == []
    client.fetch_me.assert_called_once_with("tok")


def test_attach_and_create_after_allow() -> None:
    store = _store()
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    client = MagicMock()
    client.fetch_me.return_value = {"data": {"identity_verified": True}}
    gate = IdentityVerifiedWriteGate(client)
    attach_thread_if_allowed(store, gate, "tok", key)
    comment = create_comment_if_allowed(store, gate, "tok", key, "ok")
    assert comment.body == "ok"
    assert store.get_thread(key) is not None
