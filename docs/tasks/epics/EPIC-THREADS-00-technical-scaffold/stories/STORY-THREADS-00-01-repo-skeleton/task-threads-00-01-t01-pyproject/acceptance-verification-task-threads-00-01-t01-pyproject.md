# Acceptance verification — task-threads-00-01-t01-pyproject

| Field | Value |
|-------|-------|
| **Result** | **PASS** |
| **Date** | 2026-09-21T13:37:36Z |
| **Story** | STORY-THREADS-00-01-repo-skeleton |
| **Pkg** | pkg-000001 |
| **Wave** | P3 Execute |

## AC check

- [x] `[project] name = "doge-threads"`, `requires-python = ">=3.11"`, `where = ["src"]`
- [x] pytest markers include `live_integration`
- [x] `doge-threads/pyproject.toml` exists and parses as TOML

## Evidence

```text
python3 tomllib: name=doge-threads requires-python=>=3.11 where=['src']
markers=['live_integration: tests requiring SUPABASE_TEST_URL and live Supabase project']
```
