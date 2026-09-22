from __future__ import annotations

from pathlib import Path

from core.domain import ThreadKey
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_CIVIC_NAMES = frozenset({"cluster", "intake", "story"})


def test_comment_create_does_not_mutate_story_or_cluster() -> None:
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=3))
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    store.attach_thread(key)
    store.create_comment(key, "hello")
    effects = store.civic_side_effects
    assert effects.story_creates == []
    assert effects.story_mutations == []
    assert effects.cluster_mutations == []


def test_no_civic_story_or_cluster_modules_under_src() -> None:
    found = sorted(
        str(path.relative_to(_SRC_ROOT))
        for path in _SRC_ROOT.rglob("*")
        if path.is_dir() and path.name.lower() in _CIVIC_NAMES
    )
    assert found == []


def test_store_has_no_story_or_cluster_writers() -> None:
    names = dir(InMemoryDiscussionStore)
    assert "create_story" not in names
    assert "mutate_cluster" not in names
    assert "create_cluster" not in names
