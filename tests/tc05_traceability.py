"""STORY-THREADS-TC-05 scenario ids for TC-09 TRACEABILITY.

Families only: L-PG-RDY / L-PG-SCH / L-PG-RT / L-PG-UQ / L-PG-RLS / L-PG-CLN.
"""

from __future__ import annotations

TC05_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "L-PG-RDY-tables-ready",
        "L-PG-SCH-thread-threads",
        "L-PG-SCH-thread-comments",
        "L-PG-SCH-thread-reaction-marks",
        "L-PG-SCH-thread-attachment-refs",
        "L-PG-RT-attach",
        "L-PG-RT-comment",
        "L-PG-RT-mark",
        "L-PG-RT-ref",
        "L-PG-RT-second-client",
        "L-PG-UQ-dup-mark",
        "L-PG-RLS-service-role-write",
        "L-PG-CLN-prefix",
        "L-PG-CLN-optional-delete",
    }
)
