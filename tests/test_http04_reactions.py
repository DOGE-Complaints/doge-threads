"""t01–t05 — PUT /threads/issues/{issue_id}/reactions add/remove + catalog/U1/U2."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from core.api.asgi_app import app, get_api_dependencies
from core.api.dependencies import ApiDependencies
from core.application.write_gate import IdentityVerifiedWriteGate
from core.application.write_orchestrator import ThreadWriteOrchestrator
from core.config import load_config_from_env
from core.domain.knobs import FixedThreadKnobs
from core.infrastructure.in_memory_attachment_ref_store import InMemoryAttachmentRefStore
from core.infrastructure.in_memory_discussion_store import InMemoryDiscussionStore
from core.infrastructure.in_memory_reaction_marks_store import InMemoryReactionMarksStore
from threadcontext_fixtures import SAMPLE_ISSUE_ID, stub_gateway_client
from write_orchestrator_fixtures import make_orchestrator, patch_gateway

_PATH = f"/threads/issues/{SAMPLE_ISSUE_ID}/reactions"
_HEADERS = {"Authorization": "Bearer user-tok"}


def _deps(*, verified: bool) -> tuple[ApiDependencies, object]:
    orch, store, _marks, _refs, mock_http, me = make_orchestrator(verified=verified)
    config = load_config_from_env(
        {
            "APP_PROFILE": "demo",
            "DB_BACKEND": "in_memory",
            "DOGESTONIA_SCHEMA_ID": "uus_veerenni_civic",
            "GATEWAY_BASE_URL": "https://gateway.example",
        }
    )
    deps = ApiDependencies(
        config=config,
        write_orchestrator=orch,
        discussion_store=store,
        thread_knobs=store.knobs,
        identity_me=me,
        gateway=orch._gateway,
    )
    return deps, mock_http


@pytest.fixture
def reaction_env() -> Iterator[tuple[TestClient, object]]:
    deps, mock_http = _deps(verified=True)
    app.dependency_overrides[get_api_dependencies] = lambda: deps
    try:
        yield TestClient(app), mock_http
    finally:
        app.dependency_overrides.clear()


def _body(
    *,
    reaction_id: str = "acknowledge",
    op: str = "add",
    target_kind: str = "thread_root",
    comment_id: str | None = None,
) -> dict[str, object]:
    return {
        "target_kind": target_kind,
        "comment_id": comment_id,
        "reaction_id": reaction_id,
        "op": op,
    }


def test_missing_bearer_is_401(client: TestClient) -> None:
    response = client.put(_PATH, json=_body())
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_unverified_bearer_is_403() -> None:
    deps, _mock_http = _deps(verified=False)
    app.dependency_overrides[get_api_dependencies] = lambda: deps
    try:
        response = TestClient(app).put(_PATH, json=_body(), headers=_HEADERS)
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_happy_add_u2_shape(reaction_env: tuple[TestClient, object]) -> None:
    client, mock_http = reaction_env
    with patch_gateway(mock_http):
        response = client.put(_PATH, json=_body(), headers=_HEADERS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["issue_id"] == SAMPLE_ISSUE_ID
    assert data["target_kind"] == "thread_root"
    assert data["comment_id"] is None
    assert data["reaction_id"] == "acknowledge"
    assert data["op"] == "add"
    assert data["selected"] == ["acknowledge"]
    assert data["summary_marks"] == [{"reaction_id": "acknowledge", "count": 1}]
    assert data["aggregate_count"] == 1


def test_happy_remove(reaction_env: tuple[TestClient, object]) -> None:
    client, mock_http = reaction_env
    with patch_gateway(mock_http):
        client.put(_PATH, json=_body(), headers=_HEADERS)
        response = client.put(_PATH, json=_body(op="remove"), headers=_HEADERS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["op"] == "remove"
    assert data["selected"] == []
    assert data["summary_marks"] == []
    assert data["aggregate_count"] == 0


def test_unknown_id_is_domain_error(reaction_env: tuple[TestClient, object]) -> None:
    client, mock_http = reaction_env
    with patch_gateway(mock_http):
        response = client.put(_PATH, json=_body(reaction_id="not_in_v1"), headers=_HEADERS)
    assert response.status_code == 200
    assert response.json()["error"]["code"] == "DOMAIN_ERROR"


def test_agree_disagree_mutex(reaction_env: tuple[TestClient, object]) -> None:
    client, mock_http = reaction_env
    with patch_gateway(mock_http):
        first = client.put(_PATH, json=_body(reaction_id="agree"), headers=_HEADERS)
        second = client.put(_PATH, json=_body(reaction_id="disagree"), headers=_HEADERS)
    assert first.status_code == 200
    assert first.json()["data"]["selected"] == ["agree"]
    assert second.status_code == 200
    assert second.json()["error"]["code"] == "DOMAIN_ERROR"


def test_moderation_on_thread_root_rejected(
    reaction_env: tuple[TestClient, object],
) -> None:
    client, mock_http = reaction_env
    with patch_gateway(mock_http):
        response = client.put(_PATH, json=_body(reaction_id="off_topic"), headers=_HEADERS)
    assert response.status_code == 200
    assert response.json()["error"]["code"] == "DOMAIN_ERROR"


def test_capacity_from_knobs(reaction_env: tuple[TestClient, object]) -> None:
    client, mock_http = reaction_env
    with patch_gateway(mock_http):
        for reaction_id in ("acknowledge", "support", "empathy"):
            ok = client.put(_PATH, json=_body(reaction_id=reaction_id), headers=_HEADERS)
            assert ok.status_code == 200
            assert "error" not in ok.json()
        overflow = client.put(_PATH, json=_body(reaction_id="concern"), headers=_HEADERS)
    assert overflow.status_code == 200
    assert overflow.json()["error"]["code"] == "DOMAIN_ERROR"


def test_disabled_enable_from_knobs() -> None:
    knobs = FixedThreadKnobs(
        max_depth=8,
        max_reactions_per_actor=3,
        reactions_enable={"acknowledge": True},
    )
    discussion = InMemoryDiscussionStore(knobs=knobs)
    reactions = InMemoryReactionMarksStore(knobs=knobs)
    attachments = InMemoryAttachmentRefStore(knobs=knobs)
    from unittest.mock import MagicMock

    me = MagicMock()
    me.fetch_me.return_value = {
        "data": {"identity_verified": True, "supabase_user_id": "actor-1"}
    }
    gateway, mock_http = stub_gateway_client()
    orch = ThreadWriteOrchestrator(
        gateway=gateway,
        write_gate=IdentityVerifiedWriteGate(me),
        discussion_store=discussion,
        reaction_store=reactions,
        attachment_store=attachments,
    )
    config = load_config_from_env(
        {
            "APP_PROFILE": "demo",
            "DB_BACKEND": "in_memory",
            "DOGESTONIA_SCHEMA_ID": "uus_veerenni_civic",
            "GATEWAY_BASE_URL": "https://gateway.example",
        }
    )
    deps = ApiDependencies(
        config=config,
        write_orchestrator=orch,
        discussion_store=discussion,
        thread_knobs=knobs,
        identity_me=me,
        gateway=gateway,
    )
    app.dependency_overrides[get_api_dependencies] = lambda: deps
    try:
        with patch_gateway(mock_http):
            response = TestClient(app).put(
                _PATH, json=_body(reaction_id="amused"), headers=_HEADERS
            )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["error"]["code"] == "DOMAIN_ERROR"
