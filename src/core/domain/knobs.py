from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FixedThreadKnobs:
    """Injected knobs stub. Not a pack loader; 01-02 owns compose-pull."""

    max_depth: int

    def __post_init__(self) -> None:
        if self.max_depth < 1:
            raise ValueError("max_depth must be >= 1")
