from __future__ import annotations

from typing import Protocol

from core.config import AppConfig


class ThreadServiceFactory(Protocol):
    """SOA factory contract. Product service names land in REQ01."""

    @property
    def config(self) -> AppConfig:
        """Return centralized runtime configuration."""
        ...
