"""t02/t03 — GET /threads/issues/{issue_id} tree (T1) + ThreadKey.node."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from core.api.asgi_app import _clear_api_dependencies_cache, app, get_api_dependencies
from core.api.dependencies import ApiDependencies
from core.api.thread_key_builder import build_issue_thread_key
from core.config import ConfigError, load_config_from_env
from core.domain.reaction_mark import ReactionMark, ReactionTarget
from write_orchestrator_fixtures import make_orchestrator


def test_empty_tree_has_issue_id_and_no_knobs(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOGESTONIA_SCHEMA_ID", "uus_veerenni_civic")
    _clear_api_dependencies_cache()
    response = client.get("/threads/issues/issue-empty")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == {
        "issue_id": "issue-empty",
        "comments": [],
        "thread_root_reactions": {"summary_marks": [], "aggregate_count": 0},
    }
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
    assert data["thread_root_reactions"] == {"summary_marks": [], "aggregate_count": 0}
    assert data["comments"] == [
        {
            "comment_id": comment.comment_id,
            "parent_id": None,
            "depth": comment.depth,
            "body": "root body",
            "summary_marks": [],
            "aggregate_count": 0,
        }
    ]


def test_tree_with_marks_aggregates(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOGESTONIA_SCHEMA_ID", "uus_veerenni_civic")
    _clear_api_dependencies_cache()
    deps = get_api_dependencies()
    assert deps.discussion_store is not None
    assert deps.reaction_store is not None
    key = build_issue_thread_key(
        issue_id="issue-with-marks",
        schema_id=deps.config.dogestonia_schema_id,
    )
    deps.discussion_store.attach_thread(key)
    comment = deps.discussion_store.create_comment(key, "root body")
    deps.reaction_store.add_mark(
        ReactionMark(
            actor_id="actor-a",
            target=ReactionTarget(kind="thread_root", thread_key=key),
            reaction_id="acknowledge",
        )
    )
    deps.reaction_store.add_mark(
        ReactionMark(
            actor_id="actor-a",
            target=ReactionTarget(
                kind="comment", thread_key=key, comment_id=comment.comment_id
            ),
            reaction_id="agree",
        )
    )
    deps.reaction_store.add_mark(
        ReactionMark(
            actor_id="actor-b",
            target=ReactionTarget(
                kind="comment", thread_key=key, comment_id=comment.comment_id
            ),
            reaction_id="agree",
        )
    )
    response = client.get("/threads/issues/issue-with-marks")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "knobs" not in data
    assert "selected" not in data
    assert data["thread_root_reactions"] == {
        "summary_marks": [{"reaction_id": "acknowledge", "count": 1}],
        "aggregate_count": 1,
    }
    assert "selected" not in data["thread_root_reactions"]
    assert data["comments"][0]["summary_marks"] == [{"reaction_id": "agree", "count": 2}]
    assert data["comments"][0]["aggregate_count"] == 2
    assert "selected" not in data["comments"][0]


def test_tree_with_bearer_includes_selected_from_batch_marks() -> None:
    orch, store, marks, _refs, _mock_http, me = make_orchestrator(verified=True)
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
        reaction_store=marks,
        thread_knobs=store.knobs,
        identity_me=me,
        gateway=orch._gateway,
    )
    app.dependency_overrides[get_api_dependencies] = lambda: deps
    try:
        key = build_issue_thread_key(
            issue_id="issue-selected-actor",
            schema_id=deps.config.dogestonia_schema_id,
        )
        store.attach_thread(key)
        comment = store.create_comment(key, "root body")
        marks.add_mark(
            ReactionMark(
                actor_id="actor-1",
                target=ReactionTarget(kind="thread_root", thread_key=key),
                reaction_id="acknowledge",
            )
        )
        marks.add_mark(
            ReactionMark(
                actor_id="actor-1",
                target=ReactionTarget(
                    kind="comment", thread_key=key, comment_id=comment.comment_id
                ),
                reaction_id="agree",
            )
        )
        marks.add_mark(
            ReactionMark(
                actor_id="actor-b",
                target=ReactionTarget(
                    kind="comment", thread_key=key, comment_id=comment.comment_id
                ),
                reaction_id="agree",
            )
        )
        auth_client = TestClient(app)
        authed = auth_client.get(
            "/threads/issues/issue-selected-actor",
            headers={"Authorization": "Bearer user-tok"},
        )
        assert authed.status_code == 200
        data = authed.json()["data"]
        assert "knobs" not in data
        assert data["thread_root_reactions"]["selected"] == ["acknowledge"]
        assert data["comments"][0]["selected"] == ["agree"]
        assert data["thread_root_reactions"]["summary_marks"] == [
            {"reaction_id": "acknowledge", "count": 1}
        ]
        assert data["comments"][0]["aggregate_count"] == 2
        me.fetch_me.assert_called_once_with("user-tok")

        anon = auth_client.get("/threads/issues/issue-selected-actor")
        assert anon.status_code == 200
        anon_data = anon.json()["data"]
        assert "selected" not in anon_data
        assert "selected" not in anon_data["thread_root_reactions"]
        assert "selected" not in anon_data["comments"][0]
        assert anon_data["comments"][0]["aggregate_count"] == 2
    finally:
        app.dependency_overrides.clear()


def test_tree_does_not_use_orchestrator_list_reaction_marks(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOGESTONIA_SCHEMA_ID", "uus_veerenni_civic")
    _clear_api_dependencies_cache()
    deps = get_api_dependencies()
    assert deps.discussion_store is not None
    assert deps.write_orchestrator is not None

    def _boom(*_args: object, **_kwargs: object) -> list[object]:
        raise AssertionError("write_orchestrator must not be primary tree-read DI")

    monkeypatch.setattr(deps.write_orchestrator, "list_reaction_marks", _boom)
    key = build_issue_thread_key(
        issue_id="issue-no-orch-read",
        schema_id=deps.config.dogestonia_schema_id,
    )
    deps.discussion_store.attach_thread(key)
    deps.discussion_store.create_comment(key, "root body")
    response = client.get("/threads/issues/issue-no-orch-read")
    assert response.status_code == 200
    assert response.json()["data"]["comments"][0]["aggregate_count"] == 0


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
