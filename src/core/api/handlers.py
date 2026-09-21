from __future__ import annotations

from typing import Any

from core.api.dependencies import ApiDependencies
from core.api.envelope import build_success_envelope, ensure_trace_id


def handle_health(
    dependencies: ApiDependencies, trace_id: str | None = None
) -> dict[str, Any]:
    """Liveness: process is up. No persistence or schema-pack checks."""
    del dependencies
    resolved_trace_id = ensure_trace_id(trace_id)
    return build_success_envelope(
        data={"status": "ok"},
        trace_id=resolved_trace_id,
    ).as_dict()


def handle_readiness(
    dependencies: ApiDependencies, trace_id: str | None = None
) -> dict[str, Any]:
    """Readiness from DI db_ready only (no pack/schema fields)."""
    resolved_trace_id = ensure_trace_id(trace_id)
    status = "ready" if dependencies.db_ready else "degraded"
    return build_success_envelope(
        data={
            "status": status,
            "db": {
                "backend": dependencies.db_backend,
                "ready": dependencies.db_ready,
                "checks": dict(dependencies.db_checks),
            },
        },
        trace_id=resolved_trace_id,
    ).as_dict()
