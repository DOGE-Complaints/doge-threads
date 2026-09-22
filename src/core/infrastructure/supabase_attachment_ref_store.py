"""PostgREST AttachmentRefStore on `thread_attachment_refs`."""

from __future__ import annotations

from typing import Any

from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import MediaTypeNotAllowedError
from core.domain.media_floor import StubLegalMediaFloor
from core.domain.ports import MediaFloor, ThreadKnobs
from core.infrastructure.db_supabase import SupabaseDatabase
from core.infrastructure.supabase_refs_mappers import REFS_TABLE, ref_from_row, ref_to_row


class SupabaseAttachmentRefStore:
    """AttachmentRefStore via existing SupabaseDatabase. Refs only; floor in domain."""

    def __init__(
        self,
        db: SupabaseDatabase,
        knobs: ThreadKnobs,
        floor: MediaFloor | None = None,
    ) -> None:
        self._db = db
        self._knobs = knobs
        self._floor = floor or StubLegalMediaFloor()

    @property
    def knobs(self) -> ThreadKnobs:
        return self._knobs

    @property
    def floor(self) -> MediaFloor:
        return self._floor

    def accept_ref(self, ref: AttachmentRef) -> AttachmentRef:
        self._floor.honour(ref)
        allowed = self._knobs.media_allowed_types
        if allowed and ref.media_type not in allowed:
            raise MediaTypeNotAllowedError(
                f"media_type {ref.media_type!r} not in knobs.media_allowed_types"
            )
        payload = self._db._request(
            method="POST",
            path=f"/rest/v1/{REFS_TABLE}",
            json_body=ref_to_row(ref),
            prefer="return=representation",
        )
        row = _first_row(payload)
        if row is None:
            return ref
        return ref_from_row(row)

    def list_refs(self, comment_id: str) -> list[AttachmentRef]:
        payload = self._db._request(
            method="GET",
            path=f"/rest/v1/{REFS_TABLE}",
            params={
                "select": "ref_id,comment_id,media_type,floor_class",
                "comment_id": f"eq.{comment_id}",
                "order": "created_at.asc",
            },
        )
        return [ref_from_row(row) for row in _as_rows(payload)]


def _as_rows(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []


def _first_row(payload: Any) -> dict[str, Any] | None:
    rows = _as_rows(payload)
    if not rows:
        return None
    return rows[0]
