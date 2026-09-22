from __future__ import annotations

from core.application.compose_thread_context import ThreadContextComposer
from core.domain.thread_context import IssueProjection, ThreadContext
from threadcontext_fixtures import SAMPLE_SETTINGS_PAYLOAD, SAMPLE_STORY_ID


def test_compose_issue_plus_settings_no_pack_loader() -> None:
    issue = IssueProjection(issue_id="iss-1", opaque_story_ids=(SAMPLE_STORY_ID,))
    context = ThreadContextComposer().compose(issue, SAMPLE_SETTINGS_PAYLOAD)
    assert isinstance(context, ThreadContext)
    assert context.issue is issue
    assert context.knobs.max_depth == 3
    assert context.knobs.max_reactions_per_actor == 2
    assert context.knobs.reactions_enable["like"] is True
    assert context.knobs.media_allowed_types == ("image/png",)
    mapping = context.as_mapping()
    assert mapping["issue_id"] == "iss-1"
    assert mapping["opaque_story_ids"] == [SAMPLE_STORY_ID]
    assert "story_body" not in mapping
    assert "ThreadContext" not in mapping
    assert "thread_context" not in mapping
