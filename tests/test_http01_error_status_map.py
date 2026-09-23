"""t03 — domain/auth → ErrorEnvelope + HTTP status (arch 01 + FE §3/§8)."""

from __future__ import annotations

from core.api.asgi_app import _json_http_status
from core.api.envelope import build_error_envelope
from core.api.security import UnauthorizedError
from core.domain.errors import DepthExceededError, WriteDeniedError
from core.identity.me_client import IdentityMeError


def test_unauthorized_maps_401() -> None:
    payload = build_error_envelope(UnauthorizedError("Missing Authorization Bearer token.")).as_dict()
    assert payload["error"]["code"] == "UNAUTHORIZED"
    assert payload["error"]["type"] == "auth"
    assert _json_http_status(payload) == 401


def test_write_denied_maps_403() -> None:
    payload = build_error_envelope(WriteDeniedError("denied")).as_dict()
    assert payload["error"]["code"] == "FORBIDDEN"
    assert payload["error"]["type"] == "auth"
    assert _json_http_status(payload) == 403


def test_identity_me_error_maps_403() -> None:
    payload = build_error_envelope(IdentityMeError("Identity /me timed out.")).as_dict()
    assert payload["error"]["code"] == "FORBIDDEN"
    assert _json_http_status(payload) == 403


def test_domain_error_stays_200() -> None:
    payload = build_error_envelope(DepthExceededError(3, 2)).as_dict()
    assert payload["error"]["code"] == "DOMAIN_ERROR"
    assert payload["error"]["type"] == "domain"
    assert _json_http_status(payload) == 200
