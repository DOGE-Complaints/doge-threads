from __future__ import annotations

import inspect
from pathlib import Path

from core.api.asgi_app import app
from core.application import compose_thread_context, map_shell_knobs, pull_thread_context
from core.infrastructure import providers as providers_mod


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


def test_no_pack_loader_in_threads_src() -> None:
    hits: list[str] = []
    for path in _SRC_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "pack_loader" in text or "load_pack" in text:
            hits.append(str(path.relative_to(_SRC_ROOT)))
    assert hits == []
    for module in (compose_thread_context, map_shell_knobs, pull_thread_context, providers_mod):
        source = inspect.getsource(module)
        assert "pack_loader" not in source
        assert "load_pack" not in source
        assert "shell_capabilities.json" not in source
