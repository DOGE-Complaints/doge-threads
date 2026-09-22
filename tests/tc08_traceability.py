"""STORY-THREADS-TC-08 scenario ids for TC-09 TRACEABILITY.

Families only: E-HTTP-HLTH / E-HTTP-RDY / E-HTTP-AC01.
"""

from __future__ import annotations

TC08_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "E-HTTP-HLTH-always-200",
        "E-HTTP-RDY-in-memory",
        "E-HTTP-RDY-supabase-missing-creds",
        "E-HTTP-RDY-tables-missing",
        "E-HTTP-RDY-tables-ok",
        "E-HTTP-AC01-route-set",
    }
)
