from __future__ import annotations

from asgi_public_paths import CURRENT_PUBLIC_GET_PATHS

from core.api.asgi_app import app
from core.api.dependencies import build_api_dependencies
from core.application.write_orchestrator import ThreadWriteOrchestrator
from core.infrastructure.providers import provide_service_factory


def test_factory_exposes_write_orchestrator(app_config) -> None:
    factory = provide_service_factory(app_config)
    assert isinstance(factory.write_orchestrator, ThreadWriteOrchestrator)


def test_di_wires_orchestrator_without_new_route() -> None:
    deps = build_api_dependencies()
    assert isinstance(deps.write_orchestrator, ThreadWriteOrchestrator)
    paths = sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )
    assert paths == CURRENT_PUBLIC_GET_PATHS
