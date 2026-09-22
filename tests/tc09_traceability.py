"""STORY-THREADS-TC-09 scenario ids for harness TRACEABILITY.

Families only: H-MK / H-CF / H-TR / H-GAP.
"""

from __future__ import annotations

TC09_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "H-MK-live-integration",
        "H-MK-domain-e2e",
        "H-MK-test",
        "H-MK-test-live",
        "H-MK-test-e2e-domain",
        "H-CF-default-in-memory",
        "H-CF-live-keep-supabase",
        "H-TR-matrix",
        "H-TR-rubric-9-5",
        "H-GAP-g1-g4-g6-closed",
        "H-GAP-g5-deferred",
    }
)
