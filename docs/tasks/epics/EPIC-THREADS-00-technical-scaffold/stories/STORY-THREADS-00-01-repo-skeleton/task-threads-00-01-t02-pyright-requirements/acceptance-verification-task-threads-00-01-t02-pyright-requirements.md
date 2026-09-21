# Acceptance verification — task-threads-00-01-t02-pyright-requirements

| Field | Value |
|-------|-------|
| **Result** | **PASS** |
| **Date** | 2026-09-21T13:37:36Z |
| **Story** | STORY-THREADS-00-01-repo-skeleton |
| **Pkg** | pkg-000001 |
| **Wave** | P3 Execute |

## AC check

- [x] `doge-threads/pyrightconfig.json` exists (Python 3.11)
- [x] `doge-threads/requirements.txt` lists fastapi, uvicorn, httpx
- [x] No cluster / geo / schema-packs lines

## Evidence

```text
pyrightconfig.json pythonVersion=3.11
requirements.txt: fastapi>=0.115.0 uvicorn>=0.30.0 httpx>=0.27.0
```
