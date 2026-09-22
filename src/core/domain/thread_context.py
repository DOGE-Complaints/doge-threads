from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from core.domain.errors import ThreadContextError
from core.domain.knobs import FixedThreadKnobs


@dataclass(frozen=True)
class IssueProjection:
    """Civic Issue materials. Opaque story ids only — no Story body."""

    issue_id: str
    opaque_story_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ThreadContext:
    """Logical ThreadContext composed in threads (not a gateway HTTP object)."""

    issue: IssueProjection
    knobs: FixedThreadKnobs

    def as_mapping(self) -> dict[str, Any]:
        """Serializable view without Story narrative keys."""
        return {
            "issue_id": self.issue.issue_id,
            "opaque_story_ids": list(self.issue.opaque_story_ids),
            "knobs": {
                "max_depth": self.knobs.max_depth,
                "max_reactions_per_actor": self.knobs.max_reactions_per_actor,
                "reactions_enable": dict(self.knobs.reactions_enable),
                "media_allowed_types": list(self.knobs.media_allowed_types),
            },
        }


def parse_issue_projection(
    payload: Mapping[str, Any],
    *,
    fallback_issue_id: str,
) -> IssueProjection:
    """Parse GET /node/issues/{id} envelope. Opaque story ids only."""
    issue = payload.get("issue")
    if not isinstance(issue, Mapping):
        raise ThreadContextError("issue projection missing")
    raw_id = issue.get("id") or issue.get("issue_id") or fallback_issue_id
    issue_id = str(raw_id).strip()
    if not issue_id:
        raise ThreadContextError("issue id missing")
    raw_ids = issue.get("story_ids") or ()
    opaque: list[str] = []
    if isinstance(raw_ids, (list, tuple)):
        for item in raw_ids:
            if isinstance(item, str) and item.strip():
                opaque.append(item.strip())
    return IssueProjection(issue_id=issue_id, opaque_story_ids=tuple(opaque))
