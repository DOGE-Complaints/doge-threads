from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.application.write_gate import IdentityVerifiedWriteGate, create_comment_if_allowed
from core.domain import ThreadKey, WriteDeniedError
from core.domain.knobs import FixedThreadKnobs
from core.identity.me_client import IdentityMeError
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore


def _denied(body: dict | None = None, *, error: Exception | None = None, client: object = ...) -> None:
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=3))
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    if client is ...:
        mock = MagicMock()
        if error is not None:
            mock.fetch_me.side_effect = error
        else:
            mock.fetch_me.return_value = body
        gate = IdentityVerifiedWriteGate(mock)
    else:
        gate = IdentityVerifiedWriteGate(None)
    with pytest.raises(WriteDeniedError):
        create_comment_if_allowed(store, gate, "tok", key, "nope")
    assert store.list_comments(key) == []


def test_unavailable_client_denies() -> None:
    _denied(client=None)


def test_identity_error_denies() -> None:
    _denied(error=IdentityMeError("Identity /me timed out."))


def test_none_body_denies() -> None:
    _denied(body=None)


def test_false_denies() -> None:
    _denied({"data": {"identity_verified": False}})


def test_missing_denies() -> None:
    _denied({"data": {"supabase_user_id": "u1"}})


def test_non_bool_denies() -> None:
    _denied({"data": {"identity_verified": 1}})


def test_phone_verified_only_stub_must_not_allow() -> None:
    _denied({"data": {"phone_verified": True}})


def test_account_status_active_is_not_verified() -> None:
    _denied({"data": {"account_status": "active"}})
