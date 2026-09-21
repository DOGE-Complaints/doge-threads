## Task workspace — `task-threads-00-01-t01-pyproject`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: [`doge-threads/docs/tasks/backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md`](../../../../../backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md) Scope bullet 1; [`doge-threads/docs/requirements/00-technical-scaffold.md`](../../../../../../requirements/00-technical-scaffold.md) §4 Layer 0 `pyproject.toml`
- Skill declared: `python-pro`

---
**Приоритет:** P0  
**Сложность:** S  
**Статус:** done  
**Wave:** `pkg-000001`  
**Materialized:** 2026-09-21T13:33:54Z  
---

## Task: implement — pyproject.toml (doge-threads)

### Purpose
Зафиксировать Python package manifest: `name = "doge-threads"`, setuptools `where = ["src"]`, Python ≥3.11, pytest markers including `live_integration`.

### Почему это важно (риск)
Без manifest последующие 00-02+ не могут ставить editable package и pytest `pythonpath` на `src`.

### Code Facts
1. Present: `doge-threads/pyproject.toml` — `name = "doge-threads"`, `requires-python = ">=3.11"`, `where = ["src"]`, marker `live_integration` (P3; av PASS 2026-09-21T13:37:36Z).
2. Etalon exists: `doge-complaints-gateway/pyproject.toml` — `name = "doge-complaints-gateway"`, `requires-python = ">=3.11"`, `[tool.setuptools.packages.find] where = ["src"]`, marker `live_integration`.
3. Story Scope (verbatim): `pyproject.toml` (name `doge-threads`, `where=["src"]`, Python ≥3.11, pytest markers incl. `live_integration`).

### Gap
Closed — `doge-threads/pyproject.toml` exists.

### AC/DoD
- [x] (P0) `[project] name = "doge-threads"`, `requires-python = ">=3.11"`, `[tool.setuptools.packages.find] where = ["src"]`.
- [x] (P0) pytest markers include `live_integration`.
- [x] (P0) File exists at `doge-threads/pyproject.toml` and parses as TOML.

### Where to change
- `doge-threads/pyproject.toml` (created at P3)

### Вне scope
- `src/core/**` (00-02+)
- `pyrightconfig.json` / `requirements.txt` (t02)
- CI workflow (00-06)

### Verification commands
```bash
test ! -f doge-threads/pyproject.toml && echo "pre: absent"
# after P3:
python3 -c "import tomllib; tomllib.load(open('doge-threads/pyproject.toml','rb'))"
```
