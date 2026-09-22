from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FixedThreadKnobs:
    """Injected knobs. Values arrive via 01-02 compose-pull, not a pack loader."""

    max_depth: int
    max_reactions_per_actor: int = 1
    reactions_enable: Mapping[str, bool] = field(default_factory=dict)
    media_allowed_types: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.max_depth < 1:
            raise ValueError("max_depth must be >= 1")
        if self.max_reactions_per_actor < 1:
            raise ValueError("max_reactions_per_actor must be >= 1")
