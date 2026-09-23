"""t02 — named Bearer Depends wires write-gate / Me."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from starlette.requests import Request

from core.api.asgi_app import product_write_bearer
from core.api.dependencies import ApiDependencies
from core.api.product_auth import product_write_bearer as apply_product_write_bearer
from core.api.security import UnauthorizedError
from core.config import load_config_from_env
from core.domain.errors import WriteDeniedError


def _request(authorization: str | None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if authorization is not None:
        headers.append((b"authorization", authorization.encode("latin-1")))
    return Request({"type": "http", "method": "POST", "path": "/", "headers": headers})


def _deps(*, me: object | None) -> ApiDependencies:
    return ApiDependencies(config=load_config_from_env({"APP_PROFILE": "demo"}), identity_me=me)


def test_product_write_bearer_is_named_asgi_depends() -> None:
    assert product_write_bearer.__name__ == "product_write_bearer"


def test_missing_bearer_raises_unauthorized() -> None:
    with pytest.raises(UnauthorizedError):
        apply_product_write_bearer(_request(None), _deps(me=MagicMock()))


def test_bearer_wires_write_gate_allow() -> None:
    me = MagicMock()
    me.fetch_me.return_value = {"data": {"identity_verified": True}}
    token = apply_product_write_bearer(_request("Bearer user-tok"), _deps(me=me))
    assert token == "user-tok"
    me.fetch_me.assert_called_once_with("user-tok")


def test_bearer_wires_write_gate_deny() -> None:
    me = MagicMock()
    me.fetch_me.return_value = {"data": {"identity_verified": False}}
    with pytest.raises(WriteDeniedError):
        apply_product_write_bearer(_request("Bearer user-tok"), _deps(me=me))
