# Acceptance verification — task-threads-00-01-t06-readme-gitignore

| Field | Value |
|-------|-------|
| **Result** | **PASS** |
| **Date** | 2026-09-21T13:37:36Z |
| **Story** | STORY-THREADS-00-01-repo-skeleton |
| **Pkg** | pkg-000001 |
| **Wave** | P3 Execute |

## AC check

- [x] `doge-threads/README.md` exists (short mission)
- [x] Default local port **8001** documented
- [x] `doge-threads/.gitignore` exists (venv/.env/caches; no civic pack trees)

## Evidence

```text
README.md L3: Default local port **8001**
.gitignore: .venv .env __pycache__ *.egg-info
```
