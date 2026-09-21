# Story acceptance gate — STORY-THREADS-00-01-repo-skeleton

- **Story:** Repo skeleton (pyproject, Makefile, railpack)
- **Package:** `pkg-000001-20260921-story-threads-00-01-repo-skeleton.yaml`
- **Result:** PASS
- **Date:** 2026-09-21T13:37:36Z

## AC checklist (verbatim from backlog / pipeline story)

| AC | Status | Evidence |
|----|--------|----------|
| Artifacts from REQ Layer 0 table exist under `doge-threads/` | PASS | `pyproject.toml`, `pyrightconfig.json`, `requirements.txt`, `Makefile`, `railpack.json`, `example.env`, `README.md`, `.gitignore` exist. CI workflow deferred to STORY-THREADS-00-06 (story Вне scope). No `src/` / `.github/`. |
| `railpack.json` startCommand matches uvicorn pattern (AC-THR0-08) | PASS | `python -m uvicorn --app-dir src core.api.asgi_app:app --host 0.0.0.0 --port ${PORT:-8001}` |
| Default local port documented as 8001 | PASS | `Makefile` `PORT:-8001`; `README.md` L3; `example.env` comment; `make check-env` prints `PORT = 8001` |
| `example.env` lists REQ §5 keys without inventing extra civic knobs | PASS | Keys: `APP_PROFILE`, `DB_BACKEND`, `SUPABASE_*`, `LOG_*`, `SERVICE_API_TOKEN`, `IDENTITY_BASE_URL`, `GATEWAY_BASE_URL`, `PORT`. No `CLUSTER_*` / `NODE_SCHEMA` / schema-packs. |

## Commands (live verification 2026-09-21T13:37:36Z)

```bash
python3 docs/methodology/Zeya888-builder-queue/cli/builder_resolve_queue.py --project threads --verify
python3 -c "import tomllib; tomllib.load(open('doge-threads/pyproject.toml','rb'))"
python3 -c "import json; print(json.load(open('doge-threads/railpack.json'))['deploy']['startCommand'])"
cd doge-threads && make check-env && make test
test -f doge-threads/pyrightconfig.json
test -f doge-threads/requirements.txt
test -f doge-threads/example.env
test -f doge-threads/README.md
test -f doge-threads/.gitignore
test ! -d doge-threads/src
test ! -d doge-threads/.github
```

SSOT дат: [`guides/builder-artifact-dates.md`](../../../../../../docs/methodology/Zeya888-builder-queue/guides/builder-artifact-dates.md)
