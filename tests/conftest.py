from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from core.application.factory import ThreadServiceFactory
from core.config import AppConfig, load_config_from_env
from core.infrastructure.providers import provide_service_factory
from core.logging_setup import configure_logging


@pytest.fixture(autouse=True)
def _block_dotenv_leakage(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep offline tests on in_memory and off live Supabase credentials."""
    if request.node.get_closest_marker("live_integration"):
        return
    monkeypatch.setenv("DB_BACKEND", "in_memory")
    monkeypatch.setenv("SUPABASE_URL", "")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE", "")
    from core.api.asgi_app import _clear_api_dependencies_cache

    _clear_api_dependencies_cache()


@pytest.fixture(scope="session", autouse=True)
def _pytest_session_logging() -> None:
    configure_logging(
        os.environ.get("LOG_LEVEL", "INFO"),
        log_format="text",
        log_debug_dir=None,
    )


@pytest.fixture
def app_config() -> AppConfig:
    return load_config_from_env({"APP_PROFILE": "demo", "DB_BACKEND": "in_memory"})


@pytest.fixture
def in_memory_factory(app_config: AppConfig) -> ThreadServiceFactory:
    return provide_service_factory(app_config)


@pytest.fixture
def client() -> TestClient:
    from core.api.asgi_app import _clear_api_dependencies_cache, app

    _clear_api_dependencies_cache()
    return TestClient(app)
