"""t02/t03 — C-PG-DUP-* unique mark surface; C-PG-HTTP-* fail-closed at _request."""

from __future__ import annotations

import pytest
import httpx

from core.domain.reaction_mark import ReactionMark, ReactionTarget
from core.domain.thread_key import ThreadKey
from tc03_fake_postgrest import FakeContractPostgrest, http_status_error, make_db, marks_store
from tc03_traceability import TC03_SCENARIO_IDS

_KEY = ThreadKey(node="n1", entity_type="Issue", entity_id="e1")


def _root() -> ReactionTarget:
    return ReactionTarget(kind="thread_root", thread_key=_KEY)


def _mark() -> ReactionMark:
    return ReactionMark(actor_id="a1", target=_root(), reaction_id="acknowledge")


def test_c_pg_dup_post_happy_and_store_idempotent() -> None:
    assert "C-PG-DUP-post-happy" in TC03_SCENARIO_IDS
    assert "C-PG-DUP-store-idempotent" in TC03_SCENARIO_IDS
    store, fake = marks_store()
    first = store.add_mark(_mark())
    posts_after_first = fake.posts()
    assert len(posts_after_first) == 1
    second = store.add_mark(_mark())
    # Store returns existing mark; does not POST again (raw unique not reached).
    assert second == first
    assert fake.posts() == posts_after_first


def test_c_pg_dup_fake_409_store_reraises_raw() -> None:
    assert "C-PG-DUP-fake-409" in TC03_SCENARIO_IDS
    fake = FakeContractPostgrest()
    row = {
        "actor_id": "a1",
        "node": "n1",
        "entity_type": "Issue",
        "entity_id": "e1",
        "target_kind": "thread_root",
        "comment_id": None,
        "reaction_id": "acknowledge",
    }
    fake._request(method="POST", path="/rest/v1/thread_reaction_marks", json_body=row)
    db, _wired = make_db(fake)
    with pytest.raises(httpx.HTTPStatusError) as exc:
        db._request(method="POST", path="/rest/v1/thread_reaction_marks", json_body=row)
    assert exc.value.response.status_code == 409
    # Documented: no domain UniqueError — store/db re-raises raw HTTPStatusError.


@pytest.mark.parametrize(
    ("status", "scenario"),
    [
        (401, "C-PG-HTTP-401"),
        (403, "C-PG-HTTP-403"),
        (409, "C-PG-HTTP-409"),
        (500, "C-PG-HTTP-500"),
    ],
)
def test_c_pg_http_status_fail_closed(status: int, scenario: str) -> None:
    assert scenario in TC03_SCENARIO_IDS
    store, _fake = marks_store()

    def boom(*, method: str, path: str, params=None, json_body=None, prefer=None):
        del params, json_body, prefer
        raise http_status_error(status, method=method, path=path)

    store._db._request = boom  # type: ignore[method-assign]
    with pytest.raises(httpx.HTTPStatusError) as exc:
        store.list_marks(_root())
    assert exc.value.response.status_code == status


def test_c_pg_http_timeout_fail_closed() -> None:
    assert "C-PG-HTTP-timeout" in TC03_SCENARIO_IDS
    store, _fake = marks_store()

    def boom(*, method: str, path: str, params=None, json_body=None, prefer=None):
        del method, path, params, json_body, prefer
        raise httpx.TimeoutException("stub timeout")

    store._db._request = boom  # type: ignore[method-assign]
    with pytest.raises(httpx.TimeoutException):
        store.add_mark(_mark())
