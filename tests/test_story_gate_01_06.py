from __future__ import annotations

from pathlib import Path

from core.api.asgi_app import app
from core.application.write_orchestrator import ThreadWriteOrchestrator


_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"


def test_asgi_still_health_ready_only() -> None:
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == ["/health", "/ready"]


def test_orchestrator_has_three_write_kinds() -> None:
    assert hasattr(ThreadWriteOrchestrator, "write_comment")
    assert hasattr(ThreadWriteOrchestrator, "write_reaction")
    assert hasattr(ThreadWriteOrchestrator, "write_attachment_ref")


def test_no_invented_public_write_route_in_src() -> None:
    hits: list[str] = []
    asgi = _SRC_ROOT / "core" / "api" / "asgi_app.py"
    text = asgi.read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment", "/thread"):
        if f'@app.get("{name}' in text or f'@app.post("{name}' in text:
            hits.append(name)
    assert hits == []
