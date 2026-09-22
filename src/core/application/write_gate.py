from __future__ import annotations

from core.domain.comment import Comment
from core.domain.errors import WriteDeniedError
from core.domain.ports import DiscussionStore, WriteGate
from core.domain.thread_key import Thread, ThreadKey
from core.identity.me_client import IdentityMeClient, IdentityMeError, parse_me_identity_verified


class IdentityVerifiedWriteGate:
    """Write gate: identity_verified is True only. No method-flag fallback."""

    def __init__(self, client: IdentityMeClient | None) -> None:
        self._client = client

    def allow_write(self, bearer_token: str) -> bool:
        """Fail-closed: unavailable / missing / non-bool / not True → False."""
        if self._client is None:
            return False
        try:
            body = self._client.fetch_me(bearer_token)
        except IdentityMeError:
            return False
        if body is None:
            return False
        try:
            return parse_me_identity_verified(body) is True
        except IdentityMeError:
            return False


def assert_write_allowed(gate: WriteGate, bearer_token: str) -> None:
    """Raise WriteDeniedError unless identity_verified is True."""
    if not gate.allow_write(bearer_token):
        raise WriteDeniedError("thread write denied: identity_verified is not True")


def attach_thread_if_allowed(
    store: DiscussionStore,
    gate: WriteGate,
    bearer_token: str,
    key: ThreadKey,
) -> Thread:
    """Attach a thread only after the write gate allows."""
    assert_write_allowed(gate, bearer_token)
    return store.attach_thread(key)


def create_comment_if_allowed(
    store: DiscussionStore,
    gate: WriteGate,
    bearer_token: str,
    key: ThreadKey,
    body: str,
    *,
    parent_id: str | None = None,
) -> Comment:
    """Create a comment only after the write gate allows."""
    assert_write_allowed(gate, bearer_token)
    return store.create_comment(key, body, parent_id=parent_id)
