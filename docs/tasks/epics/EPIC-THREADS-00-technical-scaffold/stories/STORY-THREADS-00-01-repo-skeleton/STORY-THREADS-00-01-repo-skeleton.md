# STORY-THREADS-00-01 — Repo skeleton (pyproject, Makefile, railpack)

## Meta
- **Key:** `STORY-THREADS-00-01-repo-skeleton`
- **Status:** Done
- **Parent Epic:** [`EPIC-THREADS-00-technical-scaffold`](../../EPIC-THREADS-00-technical-scaffold.md)
- **Parent REQ:** [`doge-threads/docs/requirements/00-technical-scaffold.md`](../../../../../requirements/00-technical-scaffold.md) §2 Layer 0, §4 Layer 0
- **source:** `backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md`
- **decision_ref:** [`doge-threads/docs/tasks/backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md`](../../../../backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md) + Parent REQ above
- **Package:** `backlog-stories/00-technical-scaffold/`
- **Siblings:** STORY-THREADS-00-02…06
- **Skill declared:** `python-pro` @ `.cursor/skills/sources/jeffallan-claude-skills/skills/python-pro/SKILL.md`
- **Depends:** —
- **Emitted:** 2026-09-21T12:19:10Z
- **Materialized:** 2026-09-21T13:33:54Z
- **Operative queue:** `threads-active-packages/pkg-000001-20260921-story-threads-00-01-repo-skeleton.yaml`

## Зачем
Создать каркас репозитория `doge-threads`, чтобы дальше класть `src/core/*` без invented civic stack. Порт по умолчанию 8001 — не конфликтовать с gateway 8000.

## Scope
- `pyproject.toml` (name `doge-threads`, `where=["src"]`, Python ≥3.11, pytest markers incl. `live_integration`)
- `pyrightconfig.json`, trimmed `requirements.txt` (fastapi, uvicorn, httpx; no cluster/geo/schema-packs)
- `Makefile`: `serve` / `dev` / `check-env` / `test`; default `PORT=8001`
- `railpack.json`: uvicorn `--app-dir src core.api.asgi_app:app`
- `example.env` keys from REQ §5 (empty values): `APP_PROFILE`, `DB_BACKEND`, `SUPABASE_*`, `LOG_*`, `SERVICE_API_TOKEN`, `IDENTITY_BASE_URL`, `GATEWAY_BASE_URL`, `PORT`
- short `README.md`, `.gitignore` (gateway class)

## Вне scope
- `src/core/**` application modules (00-02+)
- Product thread routes / DDL columns
- Civic modules; CI workflow body (00-06)

## Verified current state
| Fact | Path |
|------|------|
| No `src/` | `doge-threads/src/` absent (until 00-02+) |
| Layer 0 skeleton present | `doge-threads/pyproject.toml`, `pyrightconfig.json`, `requirements.txt`, `Makefile`, `railpack.json`, `example.env`, `README.md`, `.gitignore` (plus `LICENSE`, `docs/`) |
| Railpack etalon | `doge-complaints-gateway/railpack.json` |

## Target / AC
- [x] Artifacts from REQ Layer 0 table exist under `doge-threads/`
- [x] `railpack.json` startCommand matches uvicorn pattern (AC-THR0-08)
- [x] Default local port documented as 8001
- [x] `example.env` lists REQ §5 keys without inventing extra civic knobs

## Точки в коде (etalon)
- `doge-complaints-gateway/pyproject.toml`, `Makefile`, `railpack.json`, `example.env`

## Dependencies
- None. Blocks 00-02.

## Nested tasks

| Order | Task folder | Wave |
|-------|-------------|------|
| 1 | [`task-threads-00-01-t01-pyproject`](./task-threads-00-01-t01-pyproject/README.md) | pkg-000001 |
| 2 | [`task-threads-00-01-t02-pyright-requirements`](./task-threads-00-01-t02-pyright-requirements/README.md) | pkg-000001 |
| 3 | [`task-threads-00-01-t03-makefile-port`](./task-threads-00-01-t03-makefile-port/README.md) | pkg-000001 |
| 4 | [`task-threads-00-01-t04-railpack`](./task-threads-00-01-t04-railpack/README.md) | pkg-000001 |
| 5 | [`task-threads-00-01-t05-example-env`](./task-threads-00-01-t05-example-env/README.md) | pkg-000001 |
| 6 | [`task-threads-00-01-t06-readme-gitignore`](./task-threads-00-01-t06-readme-gitignore/README.md) | pkg-000001 |
| 7 | [`task-threads-00-01-t07-story-gate`](./task-threads-00-01-t07-story-gate/README.md) | pkg-000001 |

**Layer 0 CI** (REQ table) is out of this story — owned by `STORY-THREADS-00-06`. Gate t07 checks Layer 0 artifacts except CI.
