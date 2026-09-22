from __future__ import annotations

from typing import Protocol

from core.config import AppConfig
from core.domain.ports import DiscussionStore, ThreadKnobs, ThreadWritePort


class ThreadServiceFactory(Protocol):
    """SOA factory contract. Discussion store lands in REQ01 proofs."""

    @property
    def config(self) -> AppConfig:
        """Return centralized runtime configuration."""
        ...

    @property
    def discussion_store(self) -> DiscussionStore:
        """Return the discussion store (in_memory proofs this story)."""
        ...

    @property
    def thread_knobs(self) -> ThreadKnobs:
        """Return injected tree knobs (not a pack loader)."""
        ...

    @property
    def write_orchestrator(self) -> ThreadWritePort:
        """Return the arch §3 write orchestrator (domain API, not HTTP)."""
        ...
