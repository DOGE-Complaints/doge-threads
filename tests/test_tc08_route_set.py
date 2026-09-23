"""t03 — E-HTTP-AC01 route set == Closed HTTP-06 inventory."""

from __future__ import annotations

from asgi_public_paths import (
    CLOSED_HTTP_INVENTORY,
    CURRENT_PUBLIC_GET_PATHS,
    listed_asgi_method_paths,
)

from pathlib import Path

from core.api.asgi_app import app
from tc08_traceability import TC08_SCENARIO_IDS

_ASGI = Path(__file__).resolve().parents[1] / "src" / "core" / "api" / "asgi_app.py"


def test_e_http_ac01_route_set() -> None:
    assert "E-HTTP-AC01-route-set" in TC08_SCENARIO_IDS
    assert listed_asgi_method_paths(app) == CLOSED_HTTP_INVENTORY
    paths = sorted({path for _method, path in listed_asgi_method_paths(app)})
    assert paths == CURRENT_PUBLIC_GET_PATHS
    asgi = _ASGI.read_text(encoding="utf-8")
    assert '@app.put("/threads/issues/{issue_id}/reactions")' in asgi
    assert '@app.put("/threads/by-issue' not in asgi
    assert '@app.post("/threads/issues/{issue_id}/attachment-refs")' in asgi
    assert '@app.post("/comment' not in asgi
    assert '@app.post("/reaction' not in asgi
    assert '@app.post("/attachment' not in asgi
    assert "/threads/by-issue" not in asgi
