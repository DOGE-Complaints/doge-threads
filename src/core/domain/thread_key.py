from __future__ import annotations

from dataclasses import dataclass

# Civic first entity type is logical (arch 01-domain-logical-model). Not an owned Issue row.
CIVIC_FIRST_ENTITY_TYPE = "Issue"


@dataclass(frozen=True)
class ThreadKey:
    """External entity key for a discussion thread.

    Threads attach by this key and do not own Issue rows.
    """

    node: str
    entity_type: str
    entity_id: str

    def __post_init__(self) -> None:
        if not self.node.strip():
            raise ValueError("ThreadKey.node must be non-empty")
        if not self.entity_type.strip():
            raise ValueError("ThreadKey.entity_type must be non-empty")
        if not self.entity_id.strip():
            raise ValueError("ThreadKey.entity_id must be non-empty")


@dataclass(frozen=True)
class Thread:
    """Discussion container keyed by an external entity. Does not own Issue rows."""

    key: ThreadKey
