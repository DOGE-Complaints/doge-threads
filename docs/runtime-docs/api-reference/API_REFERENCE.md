# DOGEstonia Threads API Reference

## 1. Overview

This reference describes the runtime API surface for `doge-threads` after HTTP-06 Close:

- **As-is Closed**: Ops + public social HTTP implemented in FastAPI (`src/core/api/asgi_app.py`) and documented here.
- **Spa wire deferred**: `ThreadsSocialClient` fetch / `VITE_THREADS_BASE_URL` is a **separate spa wave** — do not implement here.

The canonical machine-readable contract is:

- [`openapi.yaml`](./openapi.yaml)

**Live OpenAPI UI is disabled:** `docs_url=None`, `redoc_url=None`, `openapi_url=None` in `asgi_app.py`. Use this folder as the contract SSOT, not `GET /docs`.

**Alias ≠ folder:** Builder Queue key `threads` → code root `doge-threads/`.

## 2. Runtime Boundary

Current runtime is **ASGI/FastAPI-driven** under `src/core/api/asgi_app.py`.

This means:

1. Operational behaviors (`health`, `ready`) are implemented and routable over HTTP.
2. The verified Closed inventory is Ops + five social routes (gate: `tests/test_tc08_route_set.py` / `CLOSED_HTTP_INVENTORY`):
   - `GET /health`
   - `GET /ready`
   - `GET /threads/knobs`
   - `GET /threads/issues/{issue_id}`
   - `POST /threads/issues/{issue_id}/comments`
   - `PUT /threads/issues/{issue_id}/reactions`
   - `POST /threads/issues/{issue_id}/attachment-refs`
3. Default local bind port is **8001** (gateway **8000**, identity **8100** — see `Makefile` / `example.env`).
4. CORS middleware (same process):

   - `allow_origins=["*"]`
   - `allow_methods=["GET", "POST", "PUT", "OPTIONS"]`
   - `allow_headers=["x-trace-id", "authorization"]`

5. Domain compose / Me / Gateway clients and write orchestrator live in `src/core/` and are reached through the social handlers above.

Do not invent superseded FE draft path prefixes.

## 3. Authentication Model

### As-is (HTTP)

`GET /health`, `GET /ready`, `GET /threads/knobs`, and `GET /threads/issues/{issue_id}` are **public**.

Write routes bind FastAPI Depends `product_write_bearer` (`asgi_app.py` / `product_auth.py`): extract `Authorization: Bearer` → `assert_write_allowed` / Me.

| Route | Auth |
|-------|------|
| `POST /threads/issues/{issue_id}/comments` | Bearer required |
| `PUT /threads/issues/{issue_id}/reactions` | Bearer required |
| `POST /threads/issues/{issue_id}/attachment-refs` | Bearer required |

[`src/core/api/security.py`](../../../src/core/api/security.py) extractors:

| Helper | Header / source |
|--------|-----------------|
| `extract_service_token` | `Authorization: Bearer …` or `X-Service-Token` |
| `extract_authorization_bearer` | `Authorization: Bearer …` |
| `extract_user_token` | `X-User-Token` (gateway etalon name) |
| `ServiceTokenAuth` / `build_service_auth_from_env` | compares against `SERVICE_API_TOKEN`; disabled when unset |

If `SERVICE_API_TOKEN` is unset, `ServiceTokenAuth` is disabled. For `APP_PROFILE=pilot`, config load fails fast when the token is missing (`src/core/config/schema.py`).

### Planned

- Formal key lifecycle policy (rotation/revocation/audit).
- Spa client wire after this Close (separate spa wave).

## 4. Envelope and Error Contract

All handler responses use a unified envelope (`src/core/api/envelope.py`):

- Success: `{ "data": { ... }, "trace_id": "..." }`
- Error: `{ "error": { "code", "type", "message", "details" }, "trace_id": "..." }`

`trace_id` is taken from request header `x-trace-id` when present and non-empty; otherwise generated (`ensure_trace_id`).

Exception → envelope mapping in `build_error_envelope`:

| Exception | `code` | `type` | HTTP (`_json_http_status`) |
|-----------|--------|--------|----------------------------|
| `UnauthorizedError` | `UNAUTHORIZED` | `auth` | **401** |
| `WriteDeniedError` / `IdentityMeError` | `FORBIDDEN` | `auth` | **403** (FE §3/§8) |
| Domain store / compose / mark / attach `*Error` | `DOMAIN_ERROR` | `domain` | **200** (arch 01) |
| `ConfigError` | `VALIDATION_ERROR` | `validation` | handler **500** |
| `ValueError` | `DOMAIN_ERROR` | `domain` | **200** |
| `ConnectionError` / `TimeoutError` / `OSError` | `INFRASTRUCTURE_ERROR` | `infrastructure` | **200** |
| other | `INTERNAL_ERROR` | `internal` | handler **500** |

Attachment floor/allowlist deny maps to `DOMAIN_ERROR` + `details.reason=attach-denied`.

CORS / `x-trace-id` stay as-is (§2). U4 origin lockdown is **out of HTTP-01**.

Validated / exercised in:

- `tests/test_tc08_health.py`
- `tests/test_tc08_ready_matrix.py`
- `tests/test_tc08_route_set.py`
- `tests/test_http06_openapi_close.py`

## 5. Ops Endpoints (as-is behavior, active HTTP binding)

### `GET /health`

- **As-is implementation**: `GET /health` in `asgi_app` → `handle_health`
- **Purpose**: liveness — process is up; no persistence checks
- **Auth**: none
- **Success example**:

```json
{
  "data": {
    "status": "ok"
  },
  "trace_id": "trace-health-1"
}
```

### `GET /ready`

- **As-is implementation**: `GET /ready` in `asgi_app` → `handle_readiness`
- **Purpose**: readiness from DI `db_ready` / `db_checks` (no schema-pack fields)
- **Auth**: none
- **HTTP status**: **200** for both `ready` and `degraded` envelopes
- **`data.status`**: `"ready"` if `dependencies.db_ready` else `"degraded"`
- **`data.db`**: `{ "backend", "ready", "checks" }` from `provide_service_factory` / `providers.py`

#### `db.checks` by backend (verified)

| `DB_BACKEND` | Condition | Typical `checks` |
|--------------|-----------|------------------|
| `in_memory` | always | `{ "in_memory": true }` → ready |
| `sqlite` | memory sqlite | `{ "connectivity": <bool> }` |
| `supabase` | missing URL or service role | `{ "credentials": false }` → degraded |
| `supabase` | credentials present | `{ "credentials": true, "tables": <bool> }` — ready iff all true |

**Ready (in_memory) example:**

```json
{
  "data": {
    "status": "ready",
    "db": {
      "backend": "in_memory",
      "ready": true,
      "checks": {
        "in_memory": true
      }
    }
  },
  "trace_id": "trace-ready-1"
}
```

**Degraded (supabase without credentials) example:**

```json
{
  "data": {
    "status": "degraded",
    "db": {
      "backend": "supabase",
      "ready": false,
      "checks": {
        "credentials": false
      }
    }
  },
  "trace_id": "trace-ready-2"
}
```

## 6. Public social HTTP (Closed, HTTP-02…05)

Documented after implement. Path table = arch `00-overview` §2. Handlers in `social_handlers.py`.

### `GET /threads/knobs`

- **Handler**: `handle_knobs` — node-level `FixedThreadKnobs` snapshot (no `issue_id`)
- **Auth**: public
- **`data`**: `{ max_depth, max_reactions_per_actor, reactions_enable, media_allowed_types }`

### `GET /threads/issues/{issue_id}`

- **Handler**: `handle_tree` → `list_comments` (T1 — comments only, no knobs)
- **Auth**: public
- **`data`**: `{ issue_id, comments: [{ comment_id, parent_id, depth, body }] }`

### `POST /threads/issues/{issue_id}/comments`

- **Handler**: `handle_create_comment` → `write_comment`
- **Auth**: Bearer
- **Body**: `{ body, parent_id }` (`parent_id` null = root)

### `PUT /threads/issues/{issue_id}/reactions`

- **Handler**: `handle_reaction` → `write_reaction` / `remove_reaction`
- **Auth**: Bearer
- **Body**: `{ target_kind, comment_id, reaction_id, op }` (`add` / `remove`)
- **`data`**: U2 `{ selected, summary_marks, aggregate_count, … }`

### `POST /threads/issues/{issue_id}/attachment-refs`

- **Handler**: `handle_create_attachment_ref` → `write_attachment_ref`
- **Auth**: Bearer
- **Body**: `{ ref_id, media_type, comment_id }` (optional `floor_class`, default `ok`)
- **Deny**: `DOMAIN_ERROR` + `details.reason=attach-denied`
- **No** multipart / blob / bytes route

## 7. Observability Notes

- `trace_id` preserved or generated in envelopes (`ensure_trace_id`).
- Startup logs `db_backend` and `profile` (`asgi_app` lifespan); warns when `DB_BACKEND=in_memory`.
- No `GET /metrics` or `GET /protected/status` routes (unlike gateway).

Sources:

- `src/core/api/envelope.py`
- `src/core/api/handlers.py`
- `src/core/api/asgi_app.py`
- `src/core/api/social_handlers.py`
- `src/core/infrastructure/providers.py`

## 8. As-is vs Deferred Summary

### As-is (Closed)

- FastAPI/ASGI runtime entrypoint.
- Envelope / error / `trace_id` consistency.
- Public Ops: `GET /health`, `GET /ready`
- Public social: knobs, tree, comments, reactions, attachment-refs
- Bearer bound on write routes.
- CORS as configured in `asgi_app`.

### Deferred (separate spa wave)

- Spa `ThreadsSocialClient` fetch / page mounts / `VITE_THREADS_BASE_URL` in spa `.env.example`
- Formal key lifecycle policy
- Optional metrics / protected status surfaces (not present)
- U4 CORS origin lockdown

## 9. Compatibility Guidance

| Consumer | Local base |
|----------|------------|
| Threads (this service) | `http://127.0.0.1:8001` |
| Gateway peer | `http://127.0.0.1:8000` (`GATEWAY_BASE_URL`) |
| Identity peer | `http://127.0.0.1:8100` (`IDENTITY_BASE_URL`) |

Operator launch: [`../manuals/server-env-quickstart.md`](../manuals/server-env-quickstart.md).

Smoke:

```bash
curl -sS http://127.0.0.1:8001/health
curl -sS -H 'x-trace-id: ops-smoke-1' http://127.0.0.1:8001/ready
```
