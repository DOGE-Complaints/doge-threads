"""STORY-THREADS-TC-07 scenario ids for TC-09 TRACEABILITY.

Families only: E-DOM-HAPPY / E-DOM-DENY.
"""

from __future__ import annotations

TC07_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "E-DOM-HAPPY-comment",
        "E-DOM-HAPPY-reaction",
        "E-DOM-HAPPY-attachment_ref",
        "E-DOM-DENY-unverified-or-missing-opaque",
    }
)
