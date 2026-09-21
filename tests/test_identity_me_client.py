from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from core.config import load_config_from_env
from core.identity.me_client import (
    IdentityMeClient,
    IdentityMeError,
    build_identity_me_from_config,
)


def test_build_identity_me_none_without_url() -> None:
    config = load_config_from_env({"APP_PROFILE": "demo"})
    assert build_identity_me_from_config(config) is None


def test_build_identity_me_from_config() -> None:
    config = load_config_from_env(
        {"APP_PROFILE": "demo", "IDENTITY_BASE_URL": "https://identity.example"}
    )
    client = build_identity_me_from_config(config)
    assert client is not None
    assert client.base_url == "https://identity.example"


def test_fetch_me_forwards_authorization_bearer() -> None:
    client = IdentityMeClient(base_url="https://identity.example")
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"data": {"ok": True}}
    mock_http = MagicMock()
    mock_http.get.return_value = response
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = False
    with patch("core.identity.me_client.httpx.Client", return_value=mock_http):
        body = client.fetch_me("user-session")
    assert body == {"data": {"ok": True}}
    mock_http.get.assert_called_once_with(
        "https://identity.example/me",
        headers={"Authorization": "Bearer user-session"},
    )


def test_fetch_me_empty_token_returns_none() -> None:
    client = IdentityMeClient(base_url="https://identity.example")
    assert client.fetch_me("   ") is None


def test_fetch_me_timeout_raises() -> None:
    client = IdentityMeClient(base_url="https://identity.example")
    mock_http = MagicMock()
    mock_http.get.side_effect = httpx.TimeoutException("boom")
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = False
    with patch("core.identity.me_client.httpx.Client", return_value=mock_http):
        with pytest.raises(IdentityMeError, match="timed out"):
            client.fetch_me("tok")
