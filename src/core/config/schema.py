from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from os import environ
from typing import Mapping


class ConfigError(ValueError):
    """Raised when environment configuration is invalid."""


class DeploymentProfile(str, Enum):
    DEMO = "demo"
    PILOT = "pilot"


@dataclass(frozen=True)
class EnvSpec:
    name: str
    required: bool
    default: str | None
    description: str


@dataclass(frozen=True)
class AppConfig:
    profile: DeploymentProfile
    db_backend: str
    supabase_url: str | None
    supabase_service_role: str | None
    log_level: str
    log_debug_dir: str | None
    log_format: str
    identity_base_url: str | None
    gateway_base_url: str | None


ENV_SCHEMA: tuple[EnvSpec, ...] = (
    EnvSpec(
        name="APP_PROFILE",
        required=False,
        default=DeploymentProfile.DEMO.value,
        description="Deployment profile: demo or pilot.",
    ),
    EnvSpec(
        name="DB_BACKEND",
        required=False,
        default="in_memory",
        description="Database backend mode: in_memory, sqlite, supabase.",
    ),
    EnvSpec(
        name="SUPABASE_URL",
        required=False,
        default=None,
        description="Supabase project URL for runtime and readiness checks.",
    ),
    EnvSpec(
        name="SUPABASE_SERVICE_ROLE",
        required=False,
        default=None,
        description="Supabase service role key for server-side access.",
    ),
    EnvSpec(
        name="LOG_LEVEL",
        required=False,
        default="INFO",
        description="Application log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
    ),
    EnvSpec(
        name="LOG_DEBUG_DIR",
        required=False,
        default=None,
        description="Directory for per-story DEBUG log files.",
    ),
    EnvSpec(
        name="LOG_FORMAT",
        required=False,
        default="text",
        description="Stdout log format: text | json.",
    ),
    EnvSpec(
        name="SERVICE_API_TOKEN",
        required=False,
        default=None,
        description=(
            "Service-to-service API token for protected operations. "
            "Required for pilot profile strict auth mode."
        ),
    ),
    EnvSpec(
        name="IDENTITY_BASE_URL",
        required=False,
        default=None,
        description="Identity service base URL for outbound Me client.",
    ),
    EnvSpec(
        name="GATEWAY_BASE_URL",
        required=False,
        default=None,
        description="Civic gateway base URL for outbound ThreadContext pull.",
    ),
)


def _get_value(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name)
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed if trimmed else None


def _parse_profile(value: str | None) -> DeploymentProfile:
    raw_value = value or DeploymentProfile.DEMO.value
    normalized = raw_value.strip().lower()
    try:
        return DeploymentProfile(normalized)
    except ValueError as exc:
        raise ConfigError(
            f"Unsupported APP_PROFILE={raw_value!r}. Expected one of: demo, pilot."
        ) from exc


_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


def _validate_http_url(url: str, *, env_name: str) -> str:
    trimmed = url.strip()
    if not trimmed:
        raise ConfigError(f"{env_name} must be a non-empty URL.")
    lower = trimmed.lower()
    if not (lower.startswith("http://") or lower.startswith("https://")):
        raise ConfigError(
            f"{env_name} must start with http:// or https://, got {url!r}."
        )
    return trimmed


def _parse_log_level(raw: str | None) -> str:
    if raw is None:
        return "INFO"
    normalized = raw.strip().upper()
    if normalized not in _LOG_LEVELS:
        raise ConfigError(
            f"Invalid LOG_LEVEL={raw!r}. Expected one of: {sorted(_LOG_LEVELS)}."
        )
    return normalized


def _parse_log_format(raw: str | None) -> str:
    if raw is None:
        return "text"
    normalized = raw.strip().lower()
    if normalized not in {"text", "json"}:
        raise ConfigError(
            f"Invalid LOG_FORMAT={raw!r}. Expected one of: ['json', 'text']."
        )
    return normalized


def _required_spec(name: str) -> EnvSpec:
    for spec in ENV_SCHEMA:
        if spec.name == name:
            return spec
    raise RuntimeError(f"Env spec for {name} not found.")


def _require_value(env: Mapping[str, str], *, name: str) -> str:
    spec = _required_spec(name)
    value = _get_value(env, name)
    if value is None:
        if spec.required and spec.default is None:
            raise ConfigError(f"Missing required environment variable: {name}.")
        if spec.default is None:
            raise ConfigError(f"Missing environment variable with no default: {name}.")
        return spec.default
    return value


def _optional_http_url(env: Mapping[str, str], *, name: str) -> str | None:
    raw = _get_value(env, name)
    if raw is None:
        return None
    return _validate_http_url(raw, env_name=name).rstrip("/")


def load_config_from_env(env: Mapping[str, str] | None = None) -> AppConfig:
    source = env or environ
    profile = _parse_profile(_get_value(source, "APP_PROFILE"))

    db_backend_raw = _require_value(source, name="DB_BACKEND")
    db_backend = db_backend_raw.strip().lower()
    if db_backend not in {"in_memory", "sqlite", "supabase"}:
        raise ConfigError(
            f"Unsupported DB_BACKEND={db_backend_raw!r}. Expected in_memory/sqlite/supabase."
        )

    log_level = _parse_log_level(_get_value(source, "LOG_LEVEL"))
    log_debug_dir = _get_value(source, "LOG_DEBUG_DIR")
    log_format = _parse_log_format(_get_value(source, "LOG_FORMAT"))

    service_api_token = _get_value(source, "SERVICE_API_TOKEN")
    if profile is DeploymentProfile.PILOT and service_api_token is None:
        raise ConfigError(
            "SERVICE_API_TOKEN is required for APP_PROFILE='pilot' strict auth mode."
        )

    return AppConfig(
        profile=profile,
        db_backend=db_backend,
        supabase_url=_get_value(source, "SUPABASE_URL"),
        supabase_service_role=_get_value(source, "SUPABASE_SERVICE_ROLE"),
        log_level=log_level,
        log_debug_dir=log_debug_dir,
        log_format=log_format,
        identity_base_url=_optional_http_url(source, name="IDENTITY_BASE_URL"),
        gateway_base_url=_optional_http_url(source, name="GATEWAY_BASE_URL"),
    )
