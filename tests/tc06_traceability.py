"""STORY-THREADS-TC-06 scenario ids for TC-09 TRACEABILITY.

Families only: L-OR-WR / L-OR-RR / L-OR-RDY.
"""

from __future__ import annotations

TC06_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "L-OR-WR-comment",
        "L-OR-WR-reaction",
        "L-OR-WR-attachment_ref",
        "L-OR-RR-comment",
        "L-OR-RR-reaction",
        "L-OR-RR-attachment_ref",
        "L-OR-RDY-ready-when-tables-ok",
        "L-OR-RDY-degraded-documented",
    }
)
