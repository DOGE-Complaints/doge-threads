## Task workspace — `task-threads-00-01-t04-railpack`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: backlog STORY-THREADS-00-01 Scope bullet 4 + AC-THR0-08; REQ0 §8 item 8
- Skill declared: `python-pro`

---
**Приоритет:** P0  
**Сложность:** S  
**Статус:** done  
**Wave:** `pkg-000001`  
**Materialized:** 2026-09-21T13:33:54Z  
---

## Task: implement — railpack.json uvicorn startCommand

### Purpose
Добавить `railpack.json` с uvicorn `--app-dir src core.api.asgi_app:app` (AC-THR0-08). Порт из env (local default 8001 belongs to Makefile/docs; do not invent civic deploy knobs).

### Code Facts
1. Present: `doge-threads/railpack.json` — `startCommand`: `python -m uvicorn --app-dir src core.api.asgi_app:app --host 0.0.0.0 --port ${PORT:-8001}`.
2. Etalon exists: `doge-complaints-gateway/railpack.json` — `startCommand`: `python -m uvicorn --app-dir src core.api.asgi_app:app --host 0.0.0.0 --port ${PORT:-8000}`.
3. Story Scope (verbatim): `railpack.json`: uvicorn `--app-dir src core.api.asgi_app:app`.
4. AC-THR0-08 (REQ0 §8): `railpack.json` startCommand documented (uvicorn `--app-dir src core.api.asgi_app:app`).

### Gap
Closed — `doge-threads/railpack.json` exists.

### AC/DoD
- [x] (P0) `doge-threads/railpack.json` exists.
- [x] (P0) `startCommand` matches uvicorn pattern `--app-dir src core.api.asgi_app:app` (AC-THR0-08).

### Where to change
- `doge-threads/railpack.json` (created at P3)

### Вне scope
- Implementing `src/core/api/asgi_app.py` (00-03)
- Dockerfile
- Civic/cluster railpack extras

### Verification commands
```bash
test ! -f doge-threads/railpack.json && echo "pre: absent"
# after P3:
python3 -c "import json; c=json.load(open('doge-threads/railpack.json')); print(c['deploy']['startCommand'])"
```
