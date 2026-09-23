from __future__ import annotations

from core.config import ConfigError
from core.domain.thread_key import CIVIC_FIRST_ENTITY_TYPE, ThreadKey


def build_issue_thread_key(*, issue_id: str, schema_id: str | None) -> ThreadKey:
    """Build civic Issue ThreadKey. node = DOGESTONIA_SCHEMA_ID only (S1)."""
    node = (schema_id or "").strip()
    if not node:
        raise ConfigError("DOGESTONIA_SCHEMA_ID is required for ThreadKey.node")
    entity_id = issue_id.strip()
    if not entity_id:
        raise ConfigError("issue_id is required")
    return ThreadKey(
        node=node,
        entity_type=CIVIC_FIRST_ENTITY_TYPE,
        entity_id=entity_id,
    )
