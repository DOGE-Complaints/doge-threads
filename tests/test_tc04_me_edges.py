"""t03 — C-ME-* Identity /me httpx + write-gate edges (offline, no live)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.application.write_gate import IdentityVerifiedWriteGate, create_comment_if_allowed
from core.domain.errors import WriteDeniedError
from core.domain.knobs import FixedThreadKnobs
from core.domain.thread_key import ThreadKey
from core.identity.me_client import IdentityMeError
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from tc04_httpx_fixtures import stub_me_http


def _store() -> InMemoryDiscussionStore:
    return InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=3))


def _key() -> ThreadKey:
    return ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


def test_c_me_401_returns_none_and_denies() -> None:
    """C-ME-401"""
    client, mock_http = stub_me_http(status_code=401)
    with patch("core.identity.me_client.httpx.Client", return_value=mock_http):
        assert client.fetch_me("tok") is None
        store = _store()
        key = _key()
        with pytest.raises(WriteDeniedError):
            create_comment_if_allowed(store, IdentityVerifiedWriteGate(client), "tok", key, "nope")
        assert store.list_comments(key) == []
    mock_http.get.assert_called()
    assert mock_http.get.call_args.args[0] == "https://identity.example/me"


def test_c_me_500_raises_and_denies() -> None:
    """C-ME-500"""
    client, mock_http = stub_me_http(status_code=500)
    with patch("core.identity.me_client.httpx.Client", return_value=mock_http):
        with pytest.raises(IdentityMeError, match="500"):
            client.fetch_me("tok")
        store = _store()
        key = _key()
        with pytest.raises(WriteDeniedError):
            create_comment_if_allowed(store, IdentityVerifiedWriteGate(client), "tok", key, "nope")
        assert store.list_comments(key) == []


@pytest.mark.parametrize(
    ("payload", "scenario_id"),
    [
        ({"data": {"supabase_user_id": "u1"}}, "C-ME-missing"),
        ({"data": {"identity_verified": "yes"}}, "C-ME-non-bool"),
        ({"data": {"phone_verified": True}}, "C-ME-phone-only"),
    ],
)
def test_c_me_opaque_and_phone_only_deny(payload: dict, scenario_id: str) -> None:
    client, mock_http = stub_me_http(payload=payload)
    store = _store()
    key = _key()
    with patch("core.identity.me_client.httpx.Client", return_value=mock_http):
        with pytest.raises(WriteDeniedError):
            create_comment_if_allowed(store, IdentityVerifiedWriteGate(client), "tok", key, "nope")
    assert store.list_comments(key) == []
    assert scenario_id.startswith("C-ME-")


def test_c_me_true_allows_write() -> None:
    """C-ME-true"""
    client, mock_http = stub_me_http(payload={"data": {"identity_verified": True}})
    store = _store()
    key = _key()
    store.attach_thread(key)
    with patch("core.identity.me_client.httpx.Client", return_value=mock_http):
        comment = create_comment_if_allowed(
            store, IdentityVerifiedWriteGate(client), "tok", key, "ok"
        )
    assert comment.body == "ok"
    assert store.list_comments(key) == [comment]
