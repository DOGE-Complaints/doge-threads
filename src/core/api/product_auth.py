"""Named Bearer Depends for product write handlers (HTTP-01). No route bind."""

from __future__ import annotations

from fastapi import Request

from core.api.dependencies import ApiDependencies
from core.api.security import UnauthorizedError, extract_authorization_bearer
from core.application.write_gate import IdentityVerifiedWriteGate, assert_write_allowed


def require_user_bearer(request: Request) -> str:
    """Extract Authorization: Bearer or raise UnauthorizedError."""
    token = extract_authorization_bearer(request.headers)
    if not token:
        raise UnauthorizedError("Missing Authorization Bearer token.")
    return token


def product_write_bearer(request: Request, deps: ApiDependencies) -> str:
    """Bearer → existing write-gate / Me (`identity_verified`).

    FastAPI bind: Depends(get_api_dependencies) then this function.
    Do not register product social routes in HTTP-01.
    """
    token = require_user_bearer(request)
    assert_write_allowed(IdentityVerifiedWriteGate(deps.identity_me), token)
    return token
