"""t01–t05 — POST /threads/issues/{issue_id}/comments create/reply + auth/depth."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from core.api.asgi_app import app, get_api_dependencies
from core.api.dependencies import ApiDependencies
from core.config import load_config_from_env
from threadcontext_fixtures import SAMPLE_ISSUE_ID
from write_orchestrator_fixtures import make_orchestrator, patch_gateway


def _deps(*, verified: bool) -> tuple[ApiDependencies, object, object]:
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
    return deps, mock_http, store


@pytest.fixture
def comment_env() -> Iterator[tuple[TestClient, object, object]]:
    deps, mock_http, store = _deps(verified=True)
    app.dependency_overrides[get_api_dependencies] = lambda: deps
    try:
        yield TestClient(app), mock_http, store
    finally:
        app.dependency_overrides.clear()


def test_missing_bearer_is_401(client: TestClient) -> None:
    response = client.post(
        f"/threads/issues/{SAMPLE_ISSUE_ID}/comments",
        json={"body": "no auth", "parent_id": None},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_unverified_bearer_is_403() -> None:
    deps, _mock_http, _store = _deps(verified=False)
    app.dependency_overrides[get_api_dependencies] = lambda: deps
    try:
        response = TestClient(app).post(
            f"/threads/issues/{SAMPLE_ISSUE_ID}/comments",
            json={"body": "denied", "parent_id": None},
            headers={"Authorization": "Bearer user-tok"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_happy_root_comment(comment_env: tuple[TestClient, object, object]) -> None:
    client, mock_http, _store = comment_env
    with patch_gateway(mock_http):
        response = client.post(
            f"/threads/issues/{SAMPLE_ISSUE_ID}/comments",
            json={"body": "root body", "parent_id": None},
            headers={"Authorization": "Bearer user-tok"},
        )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["body"] == "root body"
    assert data["parent_id"] is None
    assert data["depth"] == 1
    assert data["comment_id"]


def test_happy_reply(comment_env: tuple[TestClient, object, object]) -> None:
    client, mock_http, _store = comment_env
    with patch_gateway(mock_http):
        root = client.post(
            f"/threads/issues/{SAMPLE_ISSUE_ID}/comments",
            json={"body": "root", "parent_id": None},
            headers={"Authorization": "Bearer user-tok"},
        )
        parent_id = root.json()["data"]["comment_id"]
        reply = client.post(
            f"/threads/issues/{SAMPLE_ISSUE_ID}/comments",
            json={"body": "reply body", "parent_id": parent_id},
            headers={"Authorization": "Bearer user-tok"},
        )
    assert reply.status_code == 200
    data = reply.json()["data"]
    assert data["body"] == "reply body"
    assert data["parent_id"] == parent_id
    assert data["depth"] == 2


def test_depth_exceeded_maps_domain_200(
    comment_env: tuple[TestClient, object, object],
) -> None:
    client, mock_http, _store = comment_env
    headers = {"Authorization": "Bearer user-tok"}
    with patch_gateway(mock_http):
        first = client.post(
            f"/threads/issues/{SAMPLE_ISSUE_ID}/comments",
            json={"body": "d1", "parent_id": None},
            headers=headers,
        )
        parent_id = first.json()["data"]["comment_id"]
        for depth_label in ("d2", "d3"):
            nested = client.post(
                f"/threads/issues/{SAMPLE_ISSUE_ID}/comments",
                json={"body": depth_label, "parent_id": parent_id},
                headers=headers,
            )
            parent_id = nested.json()["data"]["comment_id"]
        overflow = client.post(
            f"/threads/issues/{SAMPLE_ISSUE_ID}/comments",
            json={"body": "d4", "parent_id": parent_id},
            headers=headers,
        )
    assert overflow.status_code == 200
    error = overflow.json()["error"]
    assert error["code"] == "DOMAIN_ERROR"
    assert "max_depth" in error["message"]
