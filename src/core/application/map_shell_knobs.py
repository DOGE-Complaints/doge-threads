from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.domain.errors import ThreadContextError
from core.domain.knobs import FixedThreadKnobs
from core.domain.story_narrative import assert_no_story_narrative


def map_pack_shell_settings_to_knobs(payload: Mapping[str, Any]) -> FixedThreadKnobs:
    """Map pack_shell_settings.threads.* into FixedThreadKnobs (lock A)."""
    assert_no_story_narrative(payload)
    settings = payload.get("pack_shell_settings")
    if not isinstance(settings, Mapping):
        raise ThreadContextError("pack_shell_settings missing")
    assert_no_story_narrative(settings)
    threads = settings.get("threads")
    if not isinstance(threads, Mapping):
        raise ThreadContextError("pack_shell_settings.threads missing")
    tree = threads.get("tree") if isinstance(threads.get("tree"), Mapping) else {}
    reactions = (
        threads.get("reactions") if isinstance(threads.get("reactions"), Mapping) else {}
    )
    media = threads.get("media") if isinstance(threads.get("media"), Mapping) else {}
    raw_enable = reactions.get("enable")
    reactions_enable: dict[str, bool] = {}
    if isinstance(raw_enable, Mapping):
        reactions_enable = {str(key): bool(value) for key, value in raw_enable.items()}
    raw_types = media.get("allowed_types") or ()
    allowed: tuple[str, ...] = ()
    if isinstance(raw_types, (list, tuple)):
        allowed = tuple(str(item) for item in raw_types if str(item).strip())
    return FixedThreadKnobs(
        max_depth=int(tree.get("max_depth") or 1),
        max_reactions_per_actor=int(reactions.get("max_reactions_per_actor") or 1),
        reactions_enable=reactions_enable,
        media_allowed_types=allowed,
    )
