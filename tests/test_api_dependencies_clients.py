from __future__ import annotations

from fastapi.testclient import TestClient

from core.api.asgi_app import _clear_api_dependencies_cache, app
from core.api.dependencies import ApiDependencies
from core.api.security import ServiceTokenAuth
from core.config import load_config_from_env
from core.gateway.client import GatewayClient
from core.identity.me_client import IdentityMeClient


def test_api_dependencies_accepts_injected_clients() -> None:
    config = load_config_from_env({"APP_PROFILE": "demo"})
    me = IdentityMeClient(base_url="https://identity.example")
    gw = GatewayClient(base_url="https://gateway.example")
    auth = ServiceTokenAuth.from_secret("tok")
    deps = ApiDependencies(
        config=config,
        service_auth=auth,
        identity_me=me,
        gateway=gw,
    )
    assert deps.identity_me is me
    assert deps.gateway is gw
    assert deps.service_auth is auth


def test_health_public_without_token() -> None:
    _clear_api_dependencies_cache()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    paths = sorted({getattr(route, "path", None) for route in app.routes})
    assert "/health" in paths
    assert "/ready" in paths
    assert not any(
        path and "/protected" in path for path in paths if isinstance(path, str)
    )
