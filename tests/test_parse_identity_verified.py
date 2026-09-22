from __future__ import annotations

import pytest

from core.identity.me_client import IdentityMeError, parse_me_identity_verified


def test_parse_true() -> None:
    assert parse_me_identity_verified({"data": {"identity_verified": True}}) is True


def test_parse_false() -> None:
    assert parse_me_identity_verified({"data": {"identity_verified": False}}) is False


def test_parse_missing_returns_none() -> None:
    assert parse_me_identity_verified({"data": {"supabase_user_id": "u1"}}) is None


def test_parse_non_bool_raises() -> None:
    with pytest.raises(IdentityMeError, match="must be bool"):
        parse_me_identity_verified({"data": {"identity_verified": "yes"}})


def test_parse_missing_data_raises() -> None:
    with pytest.raises(IdentityMeError, match="missing data"):
        parse_me_identity_verified({"ok": True})
