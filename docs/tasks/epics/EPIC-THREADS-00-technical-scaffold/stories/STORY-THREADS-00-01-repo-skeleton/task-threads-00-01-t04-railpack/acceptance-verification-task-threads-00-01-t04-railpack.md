# Acceptance verification — task-threads-00-01-t04-railpack

| Field | Value |
|-------|-------|
| **Result** | **PASS** |
| **Date** | 2026-09-21T13:37:36Z |
| **Story** | STORY-THREADS-00-01-repo-skeleton |
| **Pkg** | pkg-000001 |
| **Wave** | P3 Execute |

## AC check

- [x] `doge-threads/railpack.json` exists
- [x] `startCommand` matches uvicorn `--app-dir src core.api.asgi_app:app` (AC-THR0-08)

## Evidence

```text
python -m uvicorn --app-dir src core.api.asgi_app:app --host 0.0.0.0 --port ${PORT:-8001}
```
