"""STORY-THREADS-TC-02 scenario ids for TC-09 TRACEABILITY.

Families only: O-WR / O-DENY / O-ENF / O-ORD.
"""

from __future__ import annotations

TC02_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "O-WR-comment-true-in_memory",
        "O-WR-comment-false-in_memory",
        "O-WR-comment-true-supabase_stub",
        "O-WR-comment-false-supabase_stub",
        "O-WR-reaction-true-in_memory",
        "O-WR-reaction-false-in_memory",
        "O-WR-reaction-true-supabase_stub",
        "O-WR-reaction-false-supabase_stub",
        "O-WR-attachment-true-in_memory",
        "O-WR-attachment-false-in_memory",
        "O-WR-attachment-true-supabase_stub",
        "O-WR-attachment-false-supabase_stub",
        "O-DENY-comment",
        "O-DENY-reaction",
        "O-DENY-attachment",
        "O-ENF-depth",
        "O-ENF-enable",
        "O-ENF-allowlist",
        "O-ENF-floor",
        "O-ORD-in_memory",
        "O-ORD-supabase_stub",
    }
)
