"""STORY-THREADS-TC-03 scenario ids for TC-09 TRACEABILITY.

Families only: C-PG-GET / C-PG-DUP / C-PG-HTTP / C-PG-BAD / C-PG-MAP.
"""

from __future__ import annotations

TC03_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "C-PG-GET-empty-thread",
        "C-PG-GET-empty-comments",
        "C-PG-GET-empty-marks",
        "C-PG-GET-empty-refs",
        "C-PG-GET-eq-node-type-id",
        "C-PG-GET-eq-comment-id",
        "C-PG-GET-is-null-root-marks",
        "C-PG-DUP-post-happy",
        "C-PG-DUP-store-idempotent",
        "C-PG-DUP-fake-409",
        "C-PG-HTTP-401",
        "C-PG-HTTP-403",
        "C-PG-HTTP-409",
        "C-PG-HTTP-500",
        "C-PG-HTTP-timeout",
        "C-PG-BAD-non-list",
        "C-PG-BAD-malformed-row",
        "C-PG-BAD-civic-stories",
        "C-PG-BAD-civic-issues",
        "C-PG-MAP-thread",
        "C-PG-MAP-comment",
        "C-PG-MAP-mark",
        "C-PG-MAP-ref",
    }
)
