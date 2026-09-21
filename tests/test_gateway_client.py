from __future__ import annotations

from unittest.mock import MagicMock, patch

from core.config import load_config_from_env
from core.gateway.client import GatewayClient, build_gateway_client_from_config


def test_build_gateway_none_without_url() -> None:
    config = load_config_from_env({"APP_PROFILE": "demo"})
    assert build_gateway_client_from_config(config) is None


def test_build_gateway_from_config() -> None:
    config = load_config_from_env(
        {"APP_PROFILE": "demo", "GATEWAY_BASE_URL": "https://gateway.example"}
    )
    client = build_gateway_client_from_config(
        config, env={"SERVICE_API_TOKEN": "svc-secret"}
    )
    assert client is not None
    assert client.base_url == "https://gateway.example"
    assert client.service_token == "svc-secret"


def test_service_headers_etalon_names() -> None:
    client = GatewayClient(base_url="https://gateway.example", service_token="svc")
    assert client.service_headers() == {
        "Authorization": "Bearer svc",
        "X-Service-Token": "svc",
    }


def test_request_stubbed_httpx_no_live() -> None:
    client = GatewayClient(base_url="https://gateway.example", service_token="svc")
    response = MagicMock()
    response.status_code = 200
    mock_http = MagicMock()
    mock_http.request.return_value = response
    mock_http.__enter__.return_value = mock_http
    mock_http.__exit__.return_value = False
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        got = client.request("GET", "/")
    assert got is response
    mock_http.request.assert_called_once_with(
        "GET",
        "https://gateway.example/",
        headers={"Authorization": "Bearer svc", "X-Service-Token": "svc"},
    )
