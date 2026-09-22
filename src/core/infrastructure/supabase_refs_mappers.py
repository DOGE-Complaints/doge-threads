"""Map AttachmentRef ↔ PostgREST JSON using 01-08 columns only."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.domain.attachment_ref import AttachmentRef

REFS_TABLE = "thread_attachment_refs"
REF_WRITE_COLUMNS: frozenset[str] = frozenset(
    {"ref_id", "comment_id", "media_type", "floor_class"}
)


def ref_to_row(ref: AttachmentRef) -> dict[str, str]:
    """Serialize a ref to `thread_attachment_refs` (no `created_at` write)."""
    row = {
        "ref_id": ref.ref_id,
        "comment_id": ref.comment_id,
        "media_type": ref.media_type,
        "floor_class": ref.floor_class,
    }
    extra = set(row) - REF_WRITE_COLUMNS
    if extra:
        raise ValueError(f"ref row invented columns: {sorted(extra)}")
    return row


def ref_from_row(row: Mapping[str, Any]) -> AttachmentRef:
    """Parse a `thread_attachment_refs` row. Extra keys (e.g. `created_at`) ignored."""
    return AttachmentRef(
        ref_id=str(row["ref_id"]),
        media_type=str(row["media_type"]),
        comment_id=str(row["comment_id"]),
        floor_class=str(row.get("floor_class") or "ok"),
    )
