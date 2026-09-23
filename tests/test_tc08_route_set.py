"""t03 — E-HTTP-AC01 route set == /health + /ready only."""

from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from pathlib import Path

from core.api.asgi_app import app
from tc08_traceability import TC08_SCENARIO_IDS

_ASGI = Path(__file__).resolve().parents[1] / "src" / "core" / "api" / "asgi_app.py"


def test_e_http_ac01_route_set() -> None:
    assert "E-HTTP-AC01-route-set" in TC08_SCENARIO_IDS
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == CURRENT_PUBLIC_GET_PATHS
    asgi = _ASGI.read_text(encoding="utf-8")
    assert '@app.post("/thread' not in asgi
    assert '@app.post("/comment' not in asgi
    assert '@app.post("/reaction' not in asgi
    assert '@app.post("/attachment' not in asgi
