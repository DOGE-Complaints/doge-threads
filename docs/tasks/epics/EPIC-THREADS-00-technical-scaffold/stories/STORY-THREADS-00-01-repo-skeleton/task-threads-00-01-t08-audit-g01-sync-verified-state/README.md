## Task workspace — `task-threads-00-01-t08-audit-g01-sync-verified-state`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: `doge-threads/docs/analysis/p4-audit-STORY-THREADS-00-01-repo-skeleton-20260921.md` G-01; P5 plan `.cursor/plans/p5_threads-00-01_gap_20260921T134150Z.plan.md`
- Skill declared: `python-pro`

---
**Приоритет:** P1  
**Сложность:** S  
**Статус:** done  
**Wave:** `run_mode=threads_00_01_audit_20260921` (pkg-000001 unchanged)  
**Materialized:** 2026-09-21T13:42:44Z  
---

## Task: fix — sync Verified current state after Layer 0 skeleton

### Purpose
Обновить §Verified current state в backlog `$storyFile` и pipeline story: диск уже содержит Layer 0 skeleton; оставить факт `No src/` до 00-02+.

### Почему это важно (риск)
Stale «LICENSE + docs only» противоречит Done AC и вводит P3/P6 в заблуждение.

### Code Facts
1. `$storyFile` §Verified current state: Layer 0 present + `No src/` — `doge-threads/docs/tasks/backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md`
2. Pipeline story table matches — `…/stories/STORY-THREADS-00-01-repo-skeleton/STORY-THREADS-00-01-repo-skeleton.md`
3. Present on disk: `doge-threads/pyproject.toml`, `pyrightconfig.json`, `requirements.txt`, `Makefile`, `railpack.json`, `example.env`, `README.md`, `.gitignore`, `LICENSE`, `docs/`
4. `doge-threads/src/` absent (until 00-02+).
5. Story Status Done; AC `[x]`; product OPEN = 0. av PASS 2026-09-21T13:45:55Z.

### Gap
Closed — both verified-state tables list Layer 0; keep `No src/`.

### AC/DoD
- [x] (P0) `$storyFile` §Verified current state lists Layer 0 files present; keeps `No src/`.
- [x] (P0) Pipeline story §Verified current state matches `$storyFile`.
- [x] (P0) Do not invent `src/core/**` or CI; do not reopen story AC as failed.

### Where to change
- `doge-threads/docs/tasks/backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md` (§Verified current state only)
- `doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/STORY-THREADS-00-01-repo-skeleton.md` (same table)

### Вне scope
- Product skeleton files (already exist)
- t01–t07 README AC refresh (t09)
- pytest / `src/core/**`

### Verification commands
```bash
# P6: after edit, both tables must mention pyproject.toml / Makefile and still say No src/
grep -n "LICENSE + docs only" doge-threads/docs/tasks/backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md && echo "FAIL stale" || echo "stale gone"
test ! -d doge-threads/src
```
