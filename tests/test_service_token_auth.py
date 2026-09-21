from __future__ import annotations

import pytest

from core.api.security import (
    ServiceTokenAuth,
    UnauthorizedError,
    extract_authorization_bearer,
    extract_service_token,
    extract_user_token,
)
from core.config import ConfigError, load_config_from_env


def test_extract_service_token_bearer() -> None:
    assert extract_service_token({"Authorization": "Bearer secret-1"}) == "secret-1"


def test_extract_service_token_x_service_token() -> None:
    assert extract_service_token({"X-Service-Token": "secret-2"}) == "secret-2"


def test_extract_user_token_etalon_header() -> None:
    assert extract_user_token({"X-User-Token": "user-abc"}) == "user-abc"


def test_extract_authorization_bearer() -> None:
    assert extract_authorization_bearer({"Authorization": "Bearer sess"}) == "sess"


def test_require_missing_token() -> None:
    auth = ServiceTokenAuth.from_secret("expected", mandatory=True)
    with pytest.raises(UnauthorizedError, match="Missing"):
        auth.require({})


def test_require_invalid_token() -> None:
    auth = ServiceTokenAuth.from_secret("expected", mandatory=True)
    with pytest.raises(UnauthorizedError, match="Invalid"):
        auth.require({"Authorization": "Bearer wrong"})


def test_require_valid_bearer() -> None:
    auth = ServiceTokenAuth.from_secret("expected", mandatory=True)
    auth.require({"Authorization": "Bearer expected"})


def test_require_valid_x_service_token() -> None:
    auth = ServiceTokenAuth.from_secret("expected", mandatory=True)
    auth.require({"X-Service-Token": "expected"})


def test_pilot_failfast_missing_service_token() -> None:
    with pytest.raises(ConfigError, match="SERVICE_API_TOKEN"):
        load_config_from_env({"APP_PROFILE": "pilot"})
