from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from core.api.security import ServiceTokenAuth, build_service_auth_from_env
from core.config import AppConfig
from core.domain.ports import ThreadWritePort
from core.gateway.client import GatewayClient, build_gateway_client_from_config
from core.identity.me_client import IdentityMeClient, build_identity_me_from_config
from core.infrastructure.providers import provide_service_factory


@dataclass(frozen=True)
class ApiDependencies:
    """DI shell for HTTP handlers. Persistence via ThreadServiceFactory (00-04)."""

    config: AppConfig
    db_backend: str = "in_memory"
    db_ready: bool = True
    db_checks: dict[str, bool] = field(default_factory=dict)
    service_auth: ServiceTokenAuth | None = None
    identity_me: IdentityMeClient | None = None
    gateway: GatewayClient | None = None
    write_orchestrator: ThreadWritePort | None = None


@lru_cache(maxsize=1)
def build_api_dependencies() -> ApiDependencies:
    """Construct the cached DI container from the SOA factory."""
    factory = provide_service_factory()
    return ApiDependencies(
        config=factory.config,
        db_backend=factory.db_backend,
        db_ready=factory.db_ready,
        db_checks=dict(factory.db_checks),
        service_auth=build_service_auth_from_env(),
        identity_me=build_identity_me_from_config(factory.config),
        gateway=build_gateway_client_from_config(factory.config),
        write_orchestrator=factory.write_orchestrator,
    )
