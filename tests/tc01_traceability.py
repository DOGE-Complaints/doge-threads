"""STORY-THREADS-TC-01 scenario ids for TC-09 TRACEABILITY.

Families only: U-KEY / U-DISC / U-MARK / U-ATT / U-GATE / U-CMP.
"""

from __future__ import annotations

from core.domain import errors as domain_errors

TC01_SCENARIO_IDS: frozenset[str] = frozenset(
    {
        "U-KEY-empty-node",
        "U-KEY-empty-type",
        "U-KEY-empty-id",
        "U-DISC-not-attached",
        "U-DISC-bad-parent",
        "U-DISC-depth-eq-max-ok",
        "U-DISC-depth-max-plus-1",
        "U-DISC-nested-chain-to-max",
        "U-DISC-civic-side-effects-empty",
        "U-MARK-unknown-id",
        "U-MARK-disabled",
        "U-MARK-agree-disagree-mutex",
        "U-MARK-moderation-on-root",
        "U-MARK-max-reactions-0",
        "U-MARK-max-reactions-1",
        "U-MARK-max-reactions-n",
        "U-MARK-emotional-on-root",
        "U-MARK-emotional-on-comment",
        "U-MARK-epistemic-on-root",
        "U-MARK-epistemic-on-comment",
        "U-MARK-catalog-smoke-enabled",
        "U-ATT-empty-ref",
        "U-ATT-empty-type",
        "U-ATT-empty-comment",
        "U-ATT-bad-floor-class",
        "U-ATT-allowlist-miss",
        "U-ATT-floor-csam",
        "U-ATT-floor-catastrophic",
        "U-ATT-floor-ok",
        "U-ATT-floor-not-disableable",
        "U-GATE-missing-identity-verified",
        "U-GATE-false",
        "U-GATE-non-bool",
        "U-GATE-phone-only",
        "U-GATE-timeout",
        "U-GATE-5xx",
        "U-GATE-true-allow",
        "U-CMP-forbidden-story",
        "U-CMP-forbidden-stories",
        "U-CMP-forbidden-story_body",
        "U-CMP-forbidden-narrative",
        "U-CMP-forbidden-original_text",
        "U-CMP-forbidden-thread_context",
        "U-CMP-forbidden-ThreadContext",
        "U-CMP-opaque-story-ids-ok",
        "U-CMP-missing-knobs-fields",
    }
)

TC01_ERROR_CLASSES: frozenset[str] = frozenset(
    name
    for name, obj in vars(domain_errors).items()
    if isinstance(obj, type) and name.endswith("Error") and issubclass(obj, Exception)
)
