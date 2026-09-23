from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

from core.api.security import UnauthorizedError
from core.config import ConfigError
from core.domain.errors import (
    AttachmentRefError,
    DiscussionStoreError,
    ReactionMarkError,
    ThreadContextError,
    WriteDeniedError,
)
from core.identity.me_client import IdentityMeError


@dataclass(frozen=True)
class ErrorBody:
    code: str
    type: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ErrorEnvelope:
    error: ErrorBody
    trace_id: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SuccessEnvelope:
    data: dict[str, Any] | None
    trace_id: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def ensure_trace_id(trace_id: str | None = None) -> str:
    """Return a non-empty trace id, generating one when the header is absent."""
    if trace_id and trace_id.strip():
        return trace_id
    return str(uuid4())


def build_success_envelope(
    data: dict[str, Any] | None, trace_id: str | None = None
) -> SuccessEnvelope:
    return SuccessEnvelope(data=data, trace_id=ensure_trace_id(trace_id))


def build_error_envelope(
    exc: Exception,
    trace_id: str | None = None,
    *,
    details: dict[str, Any] | None = None,
) -> ErrorEnvelope:
    """Map a raised exception to the slim JSON error envelope.

    Auth: UnauthorizedError → UNAUTHORIZED; WriteDeniedError / IdentityMeError
    → FORBIDDEN (FE §3/§8 verify handoff). Domain *Error → DOMAIN_ERROR.
    """
    resolved_trace_id = ensure_trace_id(trace_id)
    payload = details or {}

    if isinstance(exc, UnauthorizedError):
        return ErrorEnvelope(
            error=ErrorBody(
                code="UNAUTHORIZED",
                type="auth",
                message=str(exc) or "Unauthorized.",
                details=payload,
            ),
            trace_id=resolved_trace_id,
        )

    if isinstance(exc, (WriteDeniedError, IdentityMeError)):
        return ErrorEnvelope(
            error=ErrorBody(
                code="FORBIDDEN",
                type="auth",
                message=str(exc) or "Write denied.",
                details=payload,
            ),
            trace_id=resolved_trace_id,
        )

    if isinstance(
        exc,
        (DiscussionStoreError, ThreadContextError, ReactionMarkError, AttachmentRefError),
    ):
        return ErrorEnvelope(
            error=ErrorBody(
                code="DOMAIN_ERROR",
                type="domain",
                message=str(exc),
                details=payload,
            ),
            trace_id=resolved_trace_id,
        )

    if isinstance(exc, ConfigError):
        return ErrorEnvelope(
            error=ErrorBody(
                code="VALIDATION_ERROR",
                type="validation",
                message=str(exc),
                details=payload,
            ),
            trace_id=resolved_trace_id,
        )

    if isinstance(exc, ValueError):
        return ErrorEnvelope(
            error=ErrorBody(
                code="DOMAIN_ERROR",
                type="domain",
                message=str(exc),
                details=payload,
            ),
            trace_id=resolved_trace_id,
        )

    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return ErrorEnvelope(
            error=ErrorBody(
                code="INFRASTRUCTURE_ERROR",
                type="infrastructure",
                message=str(exc),
                details=payload,
            ),
            trace_id=resolved_trace_id,
        )

    return ErrorEnvelope(
        error=ErrorBody(
            code="INTERNAL_ERROR",
            type="internal",
            message="Unexpected internal error.",
            details=payload,
        ),
        trace_id=resolved_trace_id,
    )
