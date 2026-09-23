"""Closed public ASGI inventory after HTTP-06 (Ops + W2 social)."""

from __future__ import annotations

from typing import Any

CLOSED_HTTP_INVENTORY: list[tuple[str, str]] = sorted(
    [
        ("GET", "/health"),
        ("GET", "/ready"),
        ("GET", "/threads/knobs"),
        ("GET", "/threads/issues/{issue_id}"),
        ("POST", "/threads/issues/{issue_id}/comments"),
        ("PUT", "/threads/issues/{issue_id}/reactions"),
        ("POST", "/threads/issues/{issue_id}/attachment-refs"),
    ]
)

CURRENT_PUBLIC_GET_PATHS = sorted({path for _method, path in CLOSED_HTTP_INVENTORY})


def listed_asgi_paths(app: Any) -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def listed_asgi_method_paths(app: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not isinstance(path, str) or not methods:
            continue
        for method in methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            pairs.append((method, path))
    return sorted(pairs)
