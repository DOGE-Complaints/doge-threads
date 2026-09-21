## Task workspace — `task-threads-00-01-t05-example-env`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: backlog STORY-THREADS-00-01 Scope bullet 5 + AC example.env; REQ0 §5
- Skill declared: `python-pro`

---
**Приоритет:** P0  
**Сложность:** S  
**Статус:** done  
**Wave:** `pkg-000001`  
**Materialized:** 2026-09-21T13:33:54Z  
---

## Task: implement — example.env REQ §5 keys (empty values)

### Purpose
Создать `example.env` со ключами REQ §5 (пустые значения): `APP_PROFILE`, `DB_BACKEND`, `SUPABASE_*`, `LOG_*`, `SERVICE_API_TOKEN`, `IDENTITY_BASE_URL`, `GATEWAY_BASE_URL`, `PORT`. Без extra civic knobs.

### Code Facts
1. Present: `doge-threads/example.env` — REQ §5 keys empty; comment local PORT=8001.
2. Etalon exists: `doge-complaints-gateway/example.env` — `SUPABASE_*`, `DB_BACKEND`, `SERVICE_API_TOKEN`, commented `LOG_*`; civic/cluster/`NODE_SCHEMA` knobs present.
3. Etalon **does not** list `IDENTITY_BASE_URL` / `GATEWAY_BASE_URL` (threads REQ §5 / story Scope — not a gateway copy).
4. REQ0 §5 keys: `APP_PROFILE`, `DB_BACKEND`, `SUPABASE_URL` / service role, `LOG_*`, `SERVICE_API_TOKEN`, `IDENTITY_BASE_URL`, `GATEWAY_BASE_URL`, `PORT` (default **8001** locally).
5. Story Scope (verbatim): `example.env` keys from REQ §5 (empty values): `APP_PROFILE`, `DB_BACKEND`, `SUPABASE_*`, `LOG_*`, `SERVICE_API_TOKEN`, `IDENTITY_BASE_URL`, `GATEWAY_BASE_URL`, `PORT`.

### Gap
Closed — `doge-threads/example.env` exists.

### AC/DoD
- [x] (P0) `doge-threads/example.env` lists REQ §5 keys (empty values).
- [x] (P0) No invented extra civic knobs (no cluster / `NODE_SCHEMA` / schema-packs / intake secrets).
- [x] (P1) `PORT` documented as local default 8001 (comment or empty + comment; do not invent secrets).

### Where to change
- `doge-threads/example.env` (created at P3)

### Вне scope
- `ENV_SCHEMA` / `AppConfig` implementation (00-02)
- Real secrets
- Civic env copy from gateway

### Verification commands
```bash
test ! -f doge-threads/example.env && echo "pre: absent"
# after P3:
grep -E 'APP_PROFILE|DB_BACKEND|SUPABASE_|LOG_|SERVICE_API_TOKEN|IDENTITY_BASE_URL|GATEWAY_BASE_URL|^PORT' doge-threads/example.env
```
