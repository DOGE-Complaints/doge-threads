from __future__ import annotations

from typing import Any, Mapping

from core.domain.errors import StoryNarrativeError

# Consume sibling D19 / AC-THR-04 lock (gateway shell_settings.py).
FORBIDDEN_STORY_KEYS: frozenset[str] = frozenset(
    {
        "story",
        "stories",
        "story_body",
        "narrative",
        "original_text",
        "thread_context",
        "ThreadContext",
    }
)


def assert_no_story_narrative(payload: Mapping[str, Any] | object) -> None:
    """Reject Story narrative keys in settings, Issue payload, or composed context."""
    stack: list[Any] = [payload]
    while stack:
        cur = stack.pop()
        if isinstance(cur, Mapping):
            for key, value in cur.items():
                if str(key) in FORBIDDEN_STORY_KEYS:
                    raise StoryNarrativeError(
                        f"Story narrative field {key!r} is forbidden (AC-THR-04 / D19)"
                    )
                stack.append(value)
        elif isinstance(cur, (list, tuple)):
            stack.extend(cur)
