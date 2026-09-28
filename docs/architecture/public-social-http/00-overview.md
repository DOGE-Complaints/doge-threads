# Public social HTTP — target technical architecture (overview)

| Field | Value |
|-------|--------|
| **Focus** | Public HTTP transport for FE social ops on `doge-threads` (thin ASGI over existing domain) |
| **Story package** | [`../../tasks/backlog-stories/02-public-social-http/INDEX.md`](../../tasks/backlog-stories/02-public-social-http/INDEX.md) · STORY-THREADS-HTTP-01…06 |
| **FE contract** | [`../../../../spa-app/docs/tasks/backlog-stories/threads-feed/STORY-SPA-THR-api-requirements.md`](../../../../spa-app/docs/tasks/backlog-stories/threads-feed/STORY-SPA-THR-api-requirements.md) |
| **Domain arch (coexistence)** | [`../threads-entity-shell/00-overview.md`](../threads-entity-shell/00-overview.md) |
| **Interview** | [`../../analysis/zeya888.target-tech-arch-interview-public-social-http-2026-09-23.md`](../../analysis/zeya888.target-tech-arch-interview-public-social-http-2026-09-23.md) |
| **Recorded** | 2026-09-23T12:28:24Z |
| **Mode** | Target technical architecture of the story-package focus — **not** implementation tasks / NEW STORY / pkg |

**Levels:** story scope = HTTP-01…06 · this folder = how public HTTP is realized · work items = existing stories / P1.3 elsewhere.

---

## 1) Context & inputs

As-is public HTTP: only `GET /health` + `GET /ready` ([`asgi_app.py`](../../../src/core/api/asgi_app.py)). Domain write/list already exists (`ThreadWriteOrchestrator`, stores). Spa chrome exists; `ThreadsSocialClient` returns Unavailable until Close.

**Functional vs tech:** FE api-req + HTTP stories = ops/fields/AC · this package = transport shape, path Close targets, env/node, spa handoff.

**Packaging:** N/A (existing uvicorn / Makefile / railpack from REQ0).

---

## 2) Operator locks (interview 2026-09-23)

| ID | Decision |
|----|----------|
| **B** | Knobs = separate GET; spa init + cache + refresh |
| **T1** | Tree payload = `issue_id` + `comments[]` (+ U2 `summary_marks` / `aggregate_count`) + `thread_root_reactions`; **no knobs** |
| **K2** | Knobs path = `GET /threads/knobs` (node-level, no `issue_id`) |
| **W2** | First Close = P0 **and** P1 (all social routes in one wave) |
| **N1** | Soft REST: `by-issue` → `issues` (+ K2 knobs) |
| **M1** | `ThreadKey.node` from process env (not spa; not required gateway round-trip for node id) |
| **S1** | `node = DOGESTONIA_SCHEMA_ID`; `DOGESTONIA_SCHEMA_VERSION` in env for cross-service parity, **not** part of ThreadKey |

### Target path table (Close)

| Op | Method | Path |
|----|--------|------|
| knobs | `GET` | `/threads/knobs` |
| tree | `GET` | `/threads/issues/{issue_id}` |
| comments | `POST` | `/threads/issues/{issue_id}/comments` |
| reactions | `PUT` | `/threads/issues/{issue_id}/reactions` |
| attachment-refs | `POST` | `/threads/issues/{issue_id}/attachment-refs` |
| ops | `GET` | `/health`, `/ready` (already Closed) |

---

## 3) Target components

| Component | Responsibility | Must not |
|-----------|----------------|----------|
| Product route handlers | Thin HTTP ↔ orchestrator / stores | Second domain model |
| Transport deps | Envelope, Bearer on writes, trace, CORS | Invent new error schema |
| Node env binding | Map `DOGESTONIA_SCHEMA_ID` → `ThreadKey.node` | Require spa to send node |
| Knobs read API | Expose `FixedThreadKnobs` snapshot | Embed knobs in every tree GET |
| OpenAPI Close gate | Document Closed paths after implement | Claim Closed before routes exist |

Siblings: [`01-transport-and-auth.md`](./01-transport-and-auth.md) · [`02-routes-and-contracts.md`](./02-routes-and-contracts.md) · [`03-node-env-and-threadkey.md`](./03-node-env-and-threadkey.md) · [`04-spa-consumer-handoff.md`](./04-spa-consumer-handoff.md)

---

## 4) Primary flows

```text
Spa: GET /threads/knobs  → cache → (refresh)
Spa: GET /threads/issues/{id}  → comments + U2 summaries (T1 — no knobs)
Spa: POST .../comments | PUT .../reactions | POST .../attachment-refs
     → Bearer → identity_verified gate → orchestrator → stores
```

---

## 5) Runtime / verify / env

- Start: existing `make serve` / `make dev` / railpack (PORT 8001).
- Verify: extend route-set test beyond health/ready (HTTP-06); offline HTTP tests per story.
- Env: REQ0 keys + `DOGESTONIA_SCHEMA_ID` / `DOGESTONIA_SCHEMA_VERSION` (see `03`).

---

## 6) Open questions

| ID | Topic |
|----|--------|
| U1 | Align `max_reactions_per_actor` (domain default 1 vs FE default 3) at knobs/compose implement |
| U2 | Tree read uses U2 vocab `summary_marks` / `aggregate_count` (+ `thread_root_reactions`). PUT still has `selected` (REQ10-05). |
| U3 | Boot policy if `DOGESTONIA_SCHEMA_VERSION` empty (S1: not in ThreadKey) |
| U4 | CORS tighten beyond as-is `*` |

---

## 7) Not in this doc

- NEW STORY keys, pkg, P3 task folders, product code
- Spa `ThreadsSocialClient` implement (spa wave after Close)
- Escalade / blob / REQ8 / gateway Issue CRUD
