from __future__ import annotations

from dataclasses import dataclass

FLOOR_OK = "ok"
FLOOR_CSAM = "csam"
FLOOR_CATASTROPHIC = "catastrophic"
FLOOR_CLASSES = frozenset({FLOOR_OK, FLOOR_CSAM, FLOOR_CATASTROPHIC})
FLOOR_BLOCKED_CLASSES = frozenset({FLOOR_CSAM, FLOOR_CATASTROPHIC})


@dataclass(frozen=True)
class AttachmentRef:
    """Pointer to bytes elsewhere. Type + floor_class are policy metadata, not bytes."""

    ref_id: str
    media_type: str
    comment_id: str
    floor_class: str = FLOOR_OK

    def __post_init__(self) -> None:
        if not self.ref_id.strip():
            raise ValueError("ref_id must be non-empty")
        if not self.media_type.strip():
            raise ValueError("media_type must be non-empty")
        if not self.comment_id.strip():
            raise ValueError("comment_id must be non-empty")
        if self.floor_class not in FLOOR_CLASSES:
            raise ValueError(f"unknown floor_class: {self.floor_class}")
