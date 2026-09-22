"""STORY-THREADS-01-07 offline matrix: AC-THR-01…09 (07/09 documented non-goals)."""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.api.asgi_app import app
from core.application.pull_thread_context import (
    ISSUE_GET_PATH_TEMPLATE,
    SHELL_SETTINGS_PATH,
    pull_and_compose,
)
from core.application.write_gate import IdentityVerifiedWriteGate, create_comment_if_allowed
from core.domain import ThreadKey, WriteDeniedError
from core.domain.attachment_ref import AttachmentRef
from core.domain.errors import LegalFloorError
from core.domain.knobs import FixedThreadKnobs
from core.domain.reaction_catalog import CATALOG_REACTION_IDS, REACTION_LAYER
from core.domain.story_narrative import FORBIDDEN_STORY_KEYS, assert_no_story_narrative
from core.gateway.client import GatewayClient
from core.identity.me_client import IdentityMeClient, parse_me_identity_verified
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from threadcontext_fixtures import SAMPLE_ISSUE_ID, stub_gateway_client

_SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
_WRITE_PATHS = (
    _SRC_ROOT / "core" / "application" / "write_gate.py",
    _SRC_ROOT / "core" / "identity" / "me_client.py",
)
_FORBIDDEN_07_09 = (
    "vote_storage",
    "sanction_signal",
    "cabinet_metric",
    "drift_scor",
    "rate_limit",
    "near_dup",
    "near-duplicate",
)
_CIVIC_DIRS = frozenset({"cluster", "intake", "story"})
_FAKE_THREADCONTEXT_ROUTES = (
    "/thread-context",
    "/threadcontext",
    "/ThreadContext",
    "/node/thread-context",
)


def _asgi_paths() -> list[str]:
    return sorted(
        path
        for path in (
            getattr(route, "path", None) for route in app.routes if getattr(route, "methods", None)
        )
        if isinstance(path, str)
    )


def _src_hits(tokens: tuple[str, ...], *, roots: tuple[Path, ...] | None = None) -> list[str]:
    hits: list[str] = []
    search_roots = roots if roots is not None else (_SRC_ROOT,)
    for root in search_roots:
        paths = (root,) if root.is_file() else tuple(root.rglob("*.py"))
        for path in paths:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                if token in text:
                    rel = path.relative_to(_SRC_ROOT) if _SRC_ROOT in path.parents else path
                    hits.append(f"{rel}:{token}")
    return hits


def test_ac_thr_01_no_mandated_public_product_http() -> None:
    """AC-THR-01: Draft does not mandate a new threads public HTTP path."""
    assert _asgi_paths() == ["/health", "/ready"]
    asgi = (_SRC_ROOT / "core" / "api" / "asgi_app.py").read_text(encoding="utf-8")
    for name in ("/comment", "/reaction", "/attachment", "/thread"):
        assert f'@app.get("{name}' not in asgi
        assert f'@app.post("{name}' not in asgi


def test_ac_thr_02_no_story_cluster_or_identity_impl() -> None:
    """AC-THR-02: no Story intake, no clustering, no identity verification impl."""
    found = sorted(
        str(path.relative_to(_SRC_ROOT))
        for path in _SRC_ROOT.rglob("*")
        if path.is_dir() and path.name.lower() in _CIVIC_DIRS
    )
    assert found == []
    store_names = dir(InMemoryDiscussionStore)
    assert "create_story" not in store_names
    assert "create_cluster" not in store_names
    assert _src_hits(("phone_verified", "eid_verified"), roots=_WRITE_PATHS) == []


def test_ac_thr_05_compose_from_issue_and_shell_settings() -> None:
    """AC-THR-05: compose-from-Issue+shell-settings, not a unified ThreadContext route."""
    assert ISSUE_GET_PATH_TEMPLATE == "/node/issues/{issue_id}"
    assert SHELL_SETTINGS_PATH == "/node/shell-settings"
    pull_src = (_SRC_ROOT / "core" / "application" / "pull_thread_context.py").read_text(
        encoding="utf-8"
    )
    for fake in _FAKE_THREADCONTEXT_ROUTES:
        assert fake not in pull_src
    client, mock_http = stub_gateway_client()
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        context = pull_and_compose(client, SAMPLE_ISSUE_ID)
    mapping = context.as_mapping()
    assert mapping["issue_id"] == SAMPLE_ISSUE_ID
    assert "story_body" not in mapping
    urls = [call.args[1] for call in mock_http.request.call_args_list]
    assert any("/node/issues/" in url for url in urls)
    assert any(url.endswith("/node/shell-settings") for url in urls)
    assert not any(any(fake in url for fake in _FAKE_THREADCONTEXT_ROUTES) for url in urls)


def test_ac_thr_06_identity_verified_phone_only_stub_fails() -> None:
    """AC-THR-06: write check reads identity_verified; phone-only stub must fail."""
    assert parse_me_identity_verified({"data": {"identity_verified": True}}) is True
    assert parse_me_identity_verified({"data": {"identity_verified": False}}) is False
    store = InMemoryDiscussionStore(knobs=FixedThreadKnobs(max_depth=3))
    key = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")
    mock = MagicMock()
    mock.fetch_me.return_value = {"data": {"phone_verified": True}}
    gate = IdentityVerifiedWriteGate(mock)
    with pytest.raises(WriteDeniedError):
        create_comment_if_allowed(store, gate, "tok", key, "nope")
    assert store.list_comments(key) == []
    assert _src_hits(("phone_verified",), roots=_WRITE_PATHS) == []


def test_ac_thr_03_marks_catalog_no_voice_weight() -> None:
    """AC-THR-03: reactions.v1 catalog ids; voice-weight not required."""
    assert "acknowledge" in CATALOG_REACTION_IDS
    assert "agree" in CATALOG_REACTION_IDS
    assert "disagree" in CATALOG_REACTION_IDS
    assert "off_topic" in CATALOG_REACTION_IDS
    assert REACTION_LAYER["agree"] == "epistemic"
    assert REACTION_LAYER["off_topic"] == "moderation"
    assert _src_hits(("voice_weight",)) == []


def test_ac_thr_04_no_story_body_in_settings_or_compose() -> None:
    """AC-THR-04: Story bodies forbidden; opaque ids only."""
    assert "story_body" in FORBIDDEN_STORY_KEYS
    assert "narrative" in FORBIDDEN_STORY_KEYS
    assert "ThreadContext" in FORBIDDEN_STORY_KEYS
    client, mock_http = stub_gateway_client()
    with patch("core.gateway.client.httpx.Client", return_value=mock_http):
        context = pull_and_compose(client, SAMPLE_ISSUE_ID)
    mapping = context.as_mapping()
    assert_no_story_narrative(mapping)
    assert "story_body" not in mapping
    assert "narrative" not in mapping


def test_ac_thr_08_floor_hook_not_disableable_via_knobs() -> None:
    """AC-THR-08: legal media floor honoured; node knobs cannot disable it."""
    names = {item.name for item in fields(FixedThreadKnobs)}
    assert "media_floor_enabled" not in names
    assert "disable_media_floor" not in names
    store = InMemoryAttachmentRefStore(
        knobs=FixedThreadKnobs(max_depth=4, media_allowed_types=())
    )
    with pytest.raises(LegalFloorError):
        store.accept_ref(
            AttachmentRef(
                ref_id="blob://csam",
                media_type="image/png",
                comment_id="c1",
                floor_class="csam",
            )
        )
    assert store.list_refs("c1") == []


def test_ac_thr_07_09_documented_non_goals() -> None:
    """AC-THR-07 / AC-THR-09: votes/sanctions/metrics/drift and rate-limit/near-dup are non-goals."""
    assert _src_hits(_FORBIDDEN_07_09) == []


def test_ac_thr_01_sibling_consume_not_threads_public_route() -> None:
    """AC-THR-01 checklist: sibling service-auth / Me consume is OK."""
    assert _asgi_paths() == ["/health", "/ready"]
    assert GatewayClient.request is not None
    assert IdentityMeClient.fetch_me is not None
    assert SHELL_SETTINGS_PATH == "/node/shell-settings"
