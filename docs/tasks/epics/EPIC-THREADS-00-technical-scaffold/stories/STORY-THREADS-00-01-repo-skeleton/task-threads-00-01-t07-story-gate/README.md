## Task workspace — `task-threads-00-01-t07-story-gate`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: backlog STORY-THREADS-00-01 Target / AC (verbatim); template `docs/methodology/Zeya888-builder-queue/templates/story-acceptance-gate-template.md`
- Skill declared: `python-pro`

---
**Приоритет:** P0  
**Сложность:** S  
**Статус:** done  
**Wave:** `pkg-000001`  
**Materialized:** 2026-09-21T13:33:54Z  
---

## Task: tests — story acceptance-verification (00-01 gate)

### Purpose
Закрыть story gate: все 4 AC из backlog/pipeline **verbatim**. Написать `story-acceptance-gate-STORY-THREADS-00-01.md` по шаблону **после** live verify (P3). Date только из `--print-utc-now` той сессии.

### Code Facts
1. Pipeline story AC `[x]` — `…/STORY-THREADS-00-01-repo-skeleton.md`.
2. Template exists: `docs/methodology/Zeya888-builder-queue/templates/story-acceptance-gate-template.md`.
3. REQ Layer 0 table includes CI; story «Вне scope» defers CI to 00-06 — gate checks Layer 0 artifacts **except CI**.
4. Present: `doge-threads/pyproject.toml`, `railpack.json`, `Makefile`, `example.env`, `README.md`, `.gitignore`; gate file `story-acceptance-gate-STORY-THREADS-00-01.md` Result PASS `2026-09-21T13:37:36Z`.

### Gap
Closed — gate PASS; Layer 0 artifacts present (CI deferred 00-06).

### AC/DoD (verbatim story AC — do not rewrite)
- [x] Artifacts from REQ Layer 0 table exist under `doge-threads/`
- [x] `railpack.json` startCommand matches uvicorn pattern (AC-THR0-08)
- [x] Default local port documented as 8001
- [x] `example.env` lists REQ §5 keys without inventing extra civic knobs
- [x] Gate file written from template; Result PASS only after live evidence; CI row deferred to 00-06 (not a new AC)

### Where to change
- `doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/story-acceptance-gate-STORY-THREADS-00-01.md` (created at P3)

### Вне scope
- Implementing product files (t01–t06)
- Inventing AC
- Filling Date/PASS before live `--verify` + file checks

### Verification commands
```bash
python3 docs/methodology/Zeya888-builder-queue/cli/builder_resolve_queue.py --project threads --verify
# after P3 product + live checks:
test -f doge-threads/pyproject.toml
test -f doge-threads/pyrightconfig.json
test -f doge-threads/requirements.txt
test -f doge-threads/Makefile
test -f doge-threads/railpack.json
test -f doge-threads/example.env
test -f doge-threads/README.md
test -f doge-threads/.gitignore
# CI workflow: not required here (00-06)
```
