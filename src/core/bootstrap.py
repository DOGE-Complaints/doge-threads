from __future__ import annotations

from dataclasses import dataclass
from os import environ

from core.config.env_file import merge_dotenv_from_cwd
from core.config.schema import AppConfig, load_config_from_env
from core.logging_setup import configure_logging


@dataclass(frozen=True)
class AppBootstrap:
    config: AppConfig


def bootstrap_app() -> AppBootstrap:
    """Build config + logging skeleton. No HTTP / DI (00-03)."""
    priority = dict(environ)
    source = dict(priority)
    merge_dotenv_from_cwd(source, priority=priority)
    config = load_config_from_env(source)
    configure_logging(
        config.log_level,
        log_format=config.log_format,
        log_debug_dir=config.log_debug_dir,
    )
    return AppBootstrap(config=config)
