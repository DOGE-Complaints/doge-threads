# STORY-THREADS-00-01 — Repo skeleton (pyproject, Makefile, railpack)

## Meta
- **Key:** `STORY-THREADS-00-01-repo-skeleton`
- **Status:** Done
- **Parent REQ:** [`doge-threads/docs/requirements/00-technical-scaffold.md`](../../../../requirements/00-technical-scaffold.md) §2 Layer 0, §4 Layer 0
- **Package:** `backlog-stories/00-technical-scaffold/`
- **Siblings:** STORY-THREADS-00-02…06
- **Skill declared:** `python-pro` @ `.cursor/skills/sources/jeffallan-claude-skills/skills/python-pro/SKILL.md`
- **Depends:** —
- **Emitted:** 2026-09-21T12:19:10Z

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
