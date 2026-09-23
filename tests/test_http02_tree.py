"""t02/t03 — GET /threads/issues/{issue_id} tree (T1) + ThreadKey.node."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from core.api.asgi_app import _clear_api_dependencies_cache, get_api_dependencies
from core.api.thread_key_builder import build_issue_thread_key
from core.config import ConfigError


def test_empty_tree_has_issue_id_and_no_knobs(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOGESTONIA_SCHEMA_ID", "uus_veerenni_civic")
    _clear_api_dependencies_cache()
    response = client.get("/threads/issues/issue-empty")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == {"issue_id": "issue-empty", "comments": []}
    assert "knobs" not in data


def test_populated_tree_comments_only(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOGESTONIA_SCHEMA_ID", "uus_veerenni_civic")
    _clear_api_dependencies_cache()
    deps = get_api_dependencies()
    assert deps.discussion_store is not None
    key = build_issue_thread_key(
        issue_id="issue-populated",
        schema_id=deps.config.dogestonia_schema_id,
    )
    assert key.node == "uus_veerenni_civic"
    assert key.entity_type == "Issue"
    deps.discussion_store.attach_thread(key)
    comment = deps.discussion_store.create_comment(key, "root body")
    response = client.get("/threads/issues/issue-populated")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["issue_id"] == "issue-populated"
    assert "knobs" not in data
    assert data["comments"] == [
        {
            "comment_id": comment.comment_id,
            "parent_id": None,
            "depth": comment.depth,
            "body": "root body",
        }
    ]


def test_missing_schema_id_fail_closed(client: TestClient) -> None:
    _clear_api_dependencies_cache()
    response = client.get("/threads/issues/issue-x")
    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "DOGESTONIA_SCHEMA_ID" in error["message"]


def test_build_issue_thread_key_s1_node_is_id_only() -> None:
    key = build_issue_thread_key(issue_id="iss-1", schema_id="uus_veerenni_civic")
    assert key.node == "uus_veerenni_civic"
    assert key.entity_type == "Issue"
    assert key.entity_id == "iss-1"
    with pytest.raises(ConfigError, match="DOGESTONIA_SCHEMA_ID"):
        build_issue_thread_key(issue_id="iss-1", schema_id=None)
    with pytest.raises(ConfigError, match="DOGESTONIA_SCHEMA_ID"):
        build_issue_thread_key(issue_id="iss-1", schema_id="   ")
