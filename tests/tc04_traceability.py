"""STORY-THREADS-TC-04 scenario ids for TC-09 TRACEABILITY.

Families only: C-GW-ISS / C-GW-SET / C-ME.
"""

from __future__ import annotations

TC04_ISSUE_IDS: frozenset[str] = frozenset(
    {
        "C-GW-ISS-404",
        "C-GW-ISS-500",
        "C-GW-ISS-timeout",
        "C-GW-ISS-bad-json",
        "C-GW-ISS-missing-issue",
    }
)

TC04_SETTINGS_IDS: frozenset[str] = frozenset(
    {
        "C-GW-SET-401",
        "C-GW-SET-incomplete-pack",
        "C-GW-SET-incomplete-threads",
        "C-GW-SET-forbidden-story",
        "C-GW-SET-forbidden-stories",
        "C-GW-SET-forbidden-story_body",
        "C-GW-SET-forbidden-narrative",
        "C-GW-SET-forbidden-original_text",
        "C-GW-SET-forbidden-thread_context",
        "C-GW-SET-forbidden-ThreadContext",
    }
)

TC04_ME_IDS: frozenset[str] = frozenset(
    {
        "C-ME-401",
        "C-ME-500",
        "C-ME-missing",
        "C-ME-non-bool",
        "C-ME-phone-only",
        "C-ME-true",
    }
)

TC04_SCENARIO_IDS: frozenset[str] = TC04_ISSUE_IDS | TC04_SETTINGS_IDS | TC04_ME_IDS
