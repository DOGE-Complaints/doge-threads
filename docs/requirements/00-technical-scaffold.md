# 00. Technical scaffold — FastAPI service bootstrap (no product thread AC)

Parent: docs/requirements backlog/REQ7-DOGEstonia-Threads-Entity-Social-Governance.md §3, T-REQ7-01 (separate backend service)  
Parent-id: doge-threads-entity-social-governance  
Siblings: doge-threads/docs/requirements/01-entity-thread-core.md (depends-on: implement after this scaffold); doge-complaints-gateway/docs/requirements/52-issue-thread-context-and-node-verification.md (contract: outbound civic client for future ThreadContext **pull** — route unnamed); doge-identity-service/docs/requirements/21-verification-boolean-and-audit.md (contract: outbound Identity Me client for verified boolean — route unnamed beyond gateway etalon `/me`)  
Status: Draft — awaiting implement-scaffold wave  
Plan SSOT: docs/analysis/req7-children-completeness-and-threads-req0-infra-plan-2026-09-21.md Part B  

Дата: 2026-09-21  
Проект: doge-threads  
Фокус: **технический каркас** (API host, config, DI, persistence backends, service auth, outbound clients). **Ноль** функциональных AC тредов / реакций / голосов.

---

## 1) Goal

Поднять runnable `doge-threads` как отдельный Python/FastAPI сервис ноды по паттернам `doge-complaints-gateway` bootstrap layers, чтобы после Done этого REQ можно было писать domain stories для [`01-entity-thread-core.md`](./01-entity-thread-core.md) без invented civic stack и без второго Postgres.

Name ≠ create: этот документ **описывает** целевой каркас. Материализация `src/` — отдельная команда оператора («implement scaffold»).

---

## 2) Scope / Out of scope

### In scope (infra)

- Repo skeleton: `pyproject.toml`, `pyrightconfig.json`, `requirements.txt` (minimal), `Makefile`, `railpack.json`, `example.env`, `README.md`, `.gitignore`, offline pytest CI pattern.
- FastAPI transport: lifespan, CORS, `/health`, `/ready`, exception middleware, error envelope.
- DI: `ApiDependencies` + `build_api_dependencies()` + `@lru_cache` factory.
- Config: gateway-style `env_file.py` (no `python-dotenv`) + slim `AppConfig` / `ENV_SCHEMA`.
- SOA factory: Protocol + `in_memory` / `sqlite` / `supabase` providers (empty product repos OK).
- Persistence capability: PostgREST httpx pattern; shared Supabase project; migrations folder under `doge-threads/supabase/migrations/`.
- Inbound **service** auth: own `SERVICE_API_TOKEN` (Bearer / `X-Service-Token`).
- Outbound clients (injectable): Identity Me (`IDENTITY_BASE_URL`); civic Gateway (`GATEWAY_BASE_URL`) for future ThreadContext pull.
- Testing: `conftest`, smoke `/health` `/ready`, Makefile `test`, marker `live_integration`.

### Out of scope (this REQ)

- Thread/comment/reaction HTTP paths, JSON bodies, DB column lists (→ `01` / wire / PA.2).
- Clustering, intake, schema-packs loader, geo, promotion, taxonomy, scheduler, evidence (gateway-only).
- Separate Postgres schema or separate Supabase project.
- Local Identity JWT validator inside threads (clone gateway: Me client + service token, not JWT parse).
- Dockerfile if gateway has none — use `railpack.json`.
- Votes / sanctions / drift / cabinet metrics (→ REQ8 / other children).
- Copy of full `docs/runtime-docs/bootstrap-infrastructure/` tree (optional later story; this REQ is the SSOT runbook).

---

## 3) Verified current state

| Fact | Path |
|------|------|
| No application `src/` in threads | `doge-threads/` listing: `LICENSE`, `docs/` only |
| Bootstrap etalon index | `doge-complaints-gateway/docs/runtime-docs/bootstrap-infrastructure/README.md` |
| ASGI etalon | `doge-complaints-gateway/src/core/api/asgi_app.py` |
| Service token auth etalon | `doge-complaints-gateway/src/core/api/security.py` |
| Config etalon | `doge-complaints-gateway/src/core/config/schema.py`, `env_file.py` |
| Identity Me client etalon | `doge-complaints-gateway/src/core/identity/me_client.py` |
| Railpack etalon | `doge-complaints-gateway/railpack.json` (`uvicorn --app-dir src core.api.asgi_app:app`) |
| Product shell Draft (not infra) | `doge-threads/docs/requirements/01-entity-thread-core.md` |

Unknown: shared-secret rotation policy between threads ↔ gateway ↔ identity (ops); exact ThreadContext and Me routes beyond gateway etalon `/me` remain unnamed for product wire.

---

## 4) Target architecture

```text
┌──────────────────────────────────────────────────────┐
│  HTTP Transport          asgi_app.py                 │  FastAPI, /health /ready only (REQ0)
│                          Makefile / railpack.json    │  default PORT 8001
├──────────────────────────────────────────────────────┤
│  DI Container            dependencies.py             │  ApiDependencies, lru_cache
├──────────────────────────────────────────────────────┤
│  Config                  config/schema.py            │  slim AppConfig (no civic fields)
│                          config/env_file.py          │  copy gateway verbatim
├──────────────────────────────────────────────────────┤
│  Service Factory         application/factory.py      │  ThreadServiceFactory (names TBD in 01)
│                          infrastructure/providers.py │  in_memory | sqlite | supabase
├──────────────────────────────────────────────────────┤
│  Outbound clients        identity/me_client.py       │  IDENTITY_BASE_URL
│                          gateway/ client module      │  GATEWAY_BASE_URL (route unnamed)
├──────────────────────────────────────────────────────┤
│  Persistence             db_supabase / db_sqlite     │  shared Supabase project; thread_* only
└──────────────────────────────────────────────────────┘
```

Etalon layers to follow (read, adapt, do not invent civic modules):

| Layer | Gateway doc | Threads delta |
|-------|-------------|-----------------|
| 0 Repo skeleton | live `pyproject.toml`, Makefile, railpack | name `doge-threads`; PORT **8001**; trim cluster/geo deps |
| 1 Transport | `bootstrap-infrastructure/01-fastapi-transport.md` | empty product routes until REQ01 |
| 2 DI | `02-dependency-injection.md` | wire threads repos + Identity Me + Gateway client |
| 3 Config | `05-env-config-and-launch.md` | slim `ENV_SCHEMA` (see §5) |
| 4 SOA | `03-soa-service-factory.md` | no cluster/intake/projection/promotion |
| 5 Persistence | `04-supabase-persistence.md` | migrations in this repo; shared project URL |
| 6 Identity client | gateway `me_client.py` | same trust boundary; no JWT validator |
| 7 Testing | `06-testing-architecture.md` | add Makefile `test` (gateway lacks it) |

### Layer 0 — Repo skeleton (checklist)

| Artifact | Clone from | Threads target |
|----------|------------|----------------|
| `pyproject.toml` | gateway (`where = ["src"]`, pytest markers) | name `doge-threads`, Python ≥ 3.11 |
| `pyrightconfig.json` | gateway | same |
| `requirements.txt` | gateway trimmed | fastapi, uvicorn, httpx, … — no cluster/schema-packs/geo |
| `Makefile` | `serve` / `dev` / `check-env` / **`test`** | `PORT` default **8001** |
| `railpack.json` | gateway | `uvicorn --app-dir src core.api.asgi_app:app` (`PORT` from env) |
| `example.env` | gateway subset | see §5 |
| `README.md` | short mission | threads shell service |
| `.gitignore` | gateway class | same |
| CI | `.github/workflows/test-offline.yml` pattern | offline pytest |

### Layer 1 — FastAPI transport

| Clone | Adapt |
|-------|--------|
| `src/core/api/asgi_app.py` | lifespan, CORS, `/health`, `/ready`, exception middleware |
| `handlers.py` | `handle_health`, `handle_readiness` only |
| `envelope.py` | copy error envelope |
| `security.py` | ServiceTokenAuth + user-token **header forward** pattern (as gateway) |
| `logging_setup.py`, `bootstrap.py` | copy patterns |

### Layer 2 — DI

| Clone | Adapt |
|-------|--------|
| `api/dependencies.py` | `ApiDependencies` + `build_api_dependencies()` — threads repos + IdentityMeClient + Gateway client |
| `@lru_cache` factory | same |

### Layer 3 — Config

| Clone | Adapt |
|-------|--------|
| `config/env_file.py` | **verbatim** from gateway (no python-dotenv) |
| `config/schema.py` | slim `AppConfig` — omit cluster / NODE_SCHEMA / civic-only fields |

### Layer 4 — SOA factory

| Clone | Adapt |
|-------|--------|
| `application/factory.py` Protocol | ThreadServiceFactory (concrete names in REQ01) |
| `infrastructure/providers.py` | `in_memory` / `sqlite` / `supabase` switch |
| `infrastructure/service_factory.py` | Default factory |

**Do not clone:** cluster, intake, projection, promotion, taxonomy, schema runtime, scheduler, evidence, geo packages.

### Layer 5 — Persistence

| Clone | Adapt |
|-------|--------|
| PostgREST httpx client (`db_supabase.py` style) | thread-focused repositories only (empty stubs OK for REQ0) |
| `db_sqlite.py` + in-memory | offline tests |
| Migrations | `doge-threads/supabase/migrations/` applied to **shared** Supabase project |
| Readiness | `REQUIRED_READINESS_TABLES` = thread tables once they exist (not `stories` / `doge_issues`) |

### Layer 6 — Outbound clients

| Client | Env | Purpose |
|--------|-----|---------|
| Identity Me | `IDENTITY_BASE_URL` | fetch verified boolean (gateway `me_client.py` pattern) |
| Civic Gateway | `GATEWAY_BASE_URL` | future ThreadContext **pull** (route unnamed in this REQ) |

### Layer 7 — Testing

| Clone | Adapt |
|-------|--------|
| `tests/conftest.py` | AppConfig / in_memory factory fixtures |
| `tests/smoke/test_health.py` | `/health`, `/ready` |
| pytest marker `live_integration` | optional later |
| Makefile `test` | required for threads |

---

## 5) Env subset (REQ0)

Documented in `example.env` / `ENV_SCHEMA` (values not invented here):

| Variable | Role |
|----------|------|
| `APP_PROFILE` | `demo` \| `pilot` (fail-fast token policy as gateway) |
| `DB_BACKEND` | `in_memory` \| `sqlite` \| `supabase` |
| `SUPABASE_URL` / service role | shared node project (same DB as stories/issues) |
| `LOG_*` | level / format / debug dir as needed |
| `SERVICE_API_TOKEN` | **threads own** inbound service token |
| `IDENTITY_BASE_URL` | outbound Identity Me |
| `GATEWAY_BASE_URL` | outbound civic gateway base |
| `PORT` | default **8001** locally |

**Omit** unless a later REQ requires pack read: cluster knobs, `NODE_SCHEMA`, civic intake secrets.

---

## 6) Auth & trust boundary

1. **Inbound:** protect non-public service routes with threads `SERVICE_API_TOKEN` via `Authorization: Bearer …` or `X-Service-Token` (etalon: `doge-complaints-gateway/src/core/api/security.py`). `/health` remains public; `/ready` follows gateway readiness convention.
2. **Strict / pilot:** missing `SERVICE_API_TOKEN` at config load → fail-fast (mirror gateway `APP_PROFILE=pilot` policy in `schema.py`).
3. **No local JWT validation** of Identity tokens inside threads.
4. **Outbound Identity:** Me client; may forward end-user token header pattern as gateway (header name as etalon — do not invent a second auth scheme).
5. **Outbound Gateway:** httpx client with `GATEWAY_BASE_URL`; when calling civic, send a service token header. Whether threads token equals gateway token or is a distinct shared secret = **Open** (ops); do not invent rotation scheme here.
6. Product thread routes that need user verification = later REQ01 / wire — not this scaffold’s public surface.

---

## 7) DB / migrations process

```text
Shared Supabase project (same SUPABASE_URL as gateway node).
public.stories, public.doge_issues, …  — owned/migrated by gateway (existing).
public.<thread tables>                 — owned/migrated by doge-threads/supabase/migrations/.
No CREATE SCHEMA. No second database.
```

- Conflict avoidance: table prefix `thread_` or `thr_`.
- **Do not** invent column lists in this REQ — DDL shape → REQ01 / tech-arch after scaffold boots.
- Empty placeholder migration OK for scaffold Done if documented.
- Readiness checks expand to include thread tables once migrations exist; threads need not require civic tables for `/ready`.

---

## 8) Acceptance criteria

1. **AC-THR0-01:** `make dev` (or documented equivalent) serves FastAPI with `/health` and `/ready`.
2. **AC-THR0-02:** `AppConfig` loads from env via gateway-style `env_file` + `schema` (no pydantic-settings, no python-dotenv library).
3. **AC-THR0-03:** `DB_BACKEND=in_memory` boots without Supabase.
4. **AC-THR0-04:** `DB_BACKEND=supabase` uses shared project credentials; readiness checks thread tables once migrations exist (placeholder migration OK if documented).
5. **AC-THR0-05:** Identity Me client module exists and is injectable (calls may be stubbed in unit tests).
6. **AC-THR0-06:** Gateway outbound client module exists and is injectable (calls may be stubbed; **no** ThreadContext route mandated here).
7. **AC-THR0-07:** No civic intake/cluster/geo/schema-packs/promotion modules present.
8. **AC-THR0-08:** `railpack.json` startCommand documented (uvicorn `--app-dir src core.api.asgi_app:app`).
9. **AC-THR0-09:** Offline pytest smoke green via Makefile `test` (and/or CI offline workflow).
10. **AC-THR0-10:** This REQ does **not** define public thread HTTP paths or reaction/CRUD payloads (owned by later wire / REQ01).
11. **AC-THR0-AUTH:** Inbound rejects missing/invalid service token when strict/`pilot` policy is active (fail-fast at config and/or 401 on protected routes — mirror gateway).
12. **AC-THR0-OUT:** Both Identity Me and Gateway clients are injectable; unit tests do not require live remote services.
13. **AC-THR0-EMPTY:** Scaffold Done surface = health/ready + infra only; no product thread routes.

---

## 9) Open questions (infra only)

- Shared vs distinct service-token values between threads and gateway for civic pull (ops).
- Whether first supabase `/ready` requires a committed placeholder migration before any thread_* tables exist.
- Whether optional mirror of `docs/runtime-docs/bootstrap-infrastructure/01–06` is authored in a follow-up story.

---

## 10) Ordering

```text
REQ0 (this) → implement scaffold (code) → stories / PA.2 on REQ01 domain
             ↘ concurrent: gateway 52 / identity 21 / spa 17 shell → wire wave
```

Product Story Done ≠ this Draft file exists. Scaffold Done ≠ REQ01 Done.

## 11) Dependencies

- Etalon: `doge-complaints-gateway/docs/runtime-docs/bootstrap-infrastructure/` + live `src/core/**`.
- Plan: `docs/analysis/req7-children-completeness-and-threads-req0-infra-plan-2026-09-21.md` Part B.
- Downstream: [`01-entity-thread-core.md`](./01-entity-thread-core.md) after scaffold is implementable on disk.
- Sibling seams: gateway 52 (ThreadContext pull), identity 21 (verified boolean).
