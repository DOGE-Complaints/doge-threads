## Task workspace — `task-threads-00-01-t02-pyright-requirements`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: backlog STORY-THREADS-00-01 Scope bullet 2; REQ0 §4 Layer 0 `pyrightconfig.json` / `requirements.txt`
- Skill declared: `python-pro`

---
**Приоритет:** P0  
**Сложность:** S  
**Статус:** done  
**Wave:** `pkg-000001`  
**Materialized:** 2026-09-21T13:33:54Z  
---

## Task: implement — pyrightconfig.json + trimmed requirements.txt

### Purpose
Добавить `pyrightconfig.json` (gateway class) и trimmed `requirements.txt`: fastapi, uvicorn, httpx; без cluster/geo/schema-packs.

### Code Facts
1. Present: `doge-threads/pyrightconfig.json` (`pythonVersion` 3.11), `doge-threads/requirements.txt` (fastapi, uvicorn, httpx).
2. Etalon exists: `doge-complaints-gateway/pyrightconfig.json` (`pythonVersion` 3.11, include src/tests).
3. Etalon exists: `doge-complaints-gateway/requirements.txt` — fastapi, uvicorn, psycopg, httpx, jsonschema.
4. Story Scope (verbatim): `pyrightconfig.json`, trimmed `requirements.txt` (fastapi, uvicorn, httpx; no cluster/geo/schema-packs).

### Gap
Closed — both files exist.

### AC/DoD
- [x] (P0) `doge-threads/pyrightconfig.json` exists (gateway class / Python 3.11).
- [x] (P0) `doge-threads/requirements.txt` lists fastapi, uvicorn, httpx.
- [x] (P0) No cluster / geo / schema-packs dependency lines in threads `requirements.txt`.

### Where to change
- `doge-threads/pyrightconfig.json` (created at P3)
- `doge-threads/requirements.txt` (created at P3)

### Вне scope
- `pyproject.toml` (t01)
- Civic modules; CI (00-06)
- `src/core/**`

### Verification commands
```bash
test ! -f doge-threads/pyrightconfig.json && test ! -f doge-threads/requirements.txt && echo "pre: absent"
# after P3:
test -f doge-threads/pyrightconfig.json && test -f doge-threads/requirements.txt
```
