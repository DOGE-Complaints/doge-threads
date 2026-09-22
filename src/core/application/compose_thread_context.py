from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.application.map_shell_knobs import map_pack_shell_settings_to_knobs
from core.domain.story_narrative import assert_no_story_narrative
from core.domain.thread_context import IssueProjection, ThreadContext


class ThreadContextComposer:
    """Compose logical ThreadContext in threads. No pack loader."""

    def compose(
        self,
        issue: IssueProjection,
        settings: Mapping[str, Any],
    ) -> ThreadContext:
        """Compose Issue materials + mapped shell knobs."""
        assert_no_story_narrative(settings)
        knobs = map_pack_shell_settings_to_knobs(settings)
        context = ThreadContext(issue=issue, knobs=knobs)
        assert_no_story_narrative(context.as_mapping())
        return context
