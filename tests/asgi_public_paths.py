"""Current public ASGI GET paths after HTTP-02 (ops + knobs + tree)."""

from __future__ import annotations

from typing import Any

CURRENT_PUBLIC_GET_PATHS = [
    "/health",
    "/ready",
    "/threads/issues/{issue_id}",
    "/threads/issues/{issue_id}/comments",
    "/threads/knobs",
]


def listed_asgi_paths(app: Any) -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
