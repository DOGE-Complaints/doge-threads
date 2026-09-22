"""Offline httpx stubs for STORY-THREADS-TC-04 Gateway/Me contract edges."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import httpx

from core.gateway.client import GatewayClient
from core.identity.me_client import IdentityMeClient
from threadcontext_fixtures import fake_json_response


def stub_gateway_http(
    *,
    status_code: int = 200,
    payload: Any | None = None,
    json_error: Exception | None = None,
    timeout: bool = False,
    service_token: str | None = "svc",
) -> tuple[GatewayClient, MagicMock]:
    """GatewayClient + httpx stub. No live network."""
    client = GatewayClient(base_url="https://gateway.example", service_token=service_token)
    mock_http = MagicMock()
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = False
    if timeout:
        mock_http.request.side_effect = httpx.TimeoutException("tc04 timeout")
        return client, mock_http
    response = fake_json_response(payload if payload is not None else {}, status_code=status_code)
    if json_error is not None:
        response.json.side_effect = json_error
    mock_http.request.return_value = response
    return client, mock_http


def stub_me_http(
    *,
    status_code: int = 200,
    payload: Any | None = None,
    json_error: Exception | None = None,
) -> tuple[IdentityMeClient, MagicMock]:
    """IdentityMeClient + httpx stub. No live network."""
    client = IdentityMeClient(base_url="https://identity.example")
    mock_http = MagicMock()
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = False
    response = MagicMock()
    response.status_code = status_code
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = payload if payload is not None else {}
    mock_http.get.return_value = response
    return client, mock_http
