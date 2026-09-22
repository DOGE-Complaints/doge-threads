from __future__ import annotations

from copy import deepcopy

import pytest

from core.application.compose_thread_context import ThreadContextComposer
from core.application.map_shell_knobs import map_pack_shell_settings_to_knobs
from core.domain.errors import StoryNarrativeError
from core.domain.story_narrative import FORBIDDEN_STORY_KEYS, assert_no_story_narrative
from core.domain.thread_context import IssueProjection
from threadcontext_fixtures import SAMPLE_SETTINGS_PAYLOAD, SAMPLE_STORY_ID


@pytest.mark.parametrize("forbidden_key", sorted(FORBIDDEN_STORY_KEYS))
def test_settings_forbid_story_narrative_keys(forbidden_key: str) -> None:
    tainted = deepcopy(SAMPLE_SETTINGS_PAYLOAD)
    tainted["pack_shell_settings"][forbidden_key] = "must-reject"
    with pytest.raises(StoryNarrativeError):
        map_pack_shell_settings_to_knobs(tainted)
    with pytest.raises(StoryNarrativeError):
        ThreadContextComposer().compose(
            IssueProjection(issue_id="iss-1", opaque_story_ids=(SAMPLE_STORY_ID,)),
            tainted,
        )


def test_composed_context_has_opaque_ids_only() -> None:
    context = ThreadContextComposer().compose(
        IssueProjection(issue_id="iss-1", opaque_story_ids=(SAMPLE_STORY_ID,)),
        SAMPLE_SETTINGS_PAYLOAD,
    )
    mapping = context.as_mapping()
    assert_no_story_narrative(mapping)
    assert mapping["opaque_story_ids"] == [SAMPLE_STORY_ID]
    assert "story_body" not in mapping
    assert "narrative" not in mapping
    assert "original_text" not in mapping
