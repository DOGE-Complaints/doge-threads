## Task workspace — `task-threads-00-01-t09-audit-g02-refresh-task-readme-facts`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: `doge-threads/docs/analysis/p4-audit-STORY-THREADS-00-01-repo-skeleton-20260921.md` G-02; P5 plan `.cursor/plans/p5_threads-00-01_gap_20260921T134150Z.plan.md`
- Skill declared: `python-pro`

---
**Приоритет:** P1  
**Сложность:** S  
**Статус:** done  
**Wave:** `run_mode=threads_00_01_audit_20260921` (pkg-000001 unchanged)  
**Materialized:** 2026-09-21T13:44:18Z  
---

## Task: fix — refresh t01–t07 README AC and Code Facts

### Purpose
Привести AC/DoD чекбоксы и Code Facts в `task-threads-00-01-t01`…`t07` README в соответствие с `acceptance-verification-*.md` PASS и файлами на диске. Status уже `done`.

### Почему это важно (риск)
Неотмеченные AC и «Target absent» после P3 Done вводят аудит/P6 в заблуждение; это не product AC fail.

### Code Facts
1. t01–t07 README AC/DoD `[x]`; Gap Closed; Code Facts present (P6).
2. t01 Code Facts: Present `doge-threads/pyproject.toml` — `task-threads-00-01-t01-pyproject/README.md`.
3. `acceptance-verification-task-threads-00-01-t01-…` … `t07-…` Result **PASS** `2026-09-21T13:37:36Z`.
4. Product files present: `doge-threads/pyproject.toml`, `pyrightconfig.json`, `requirements.txt`, `Makefile`, `railpack.json`, `example.env`, `README.md`, `.gitignore`.
5. Story AC PASS; product OPEN = 0. t08 sibling av PASS 2026-09-21T13:45:55Z.

### Gap
Closed — t01–t07 README AC/Code Facts match disk + av.

### AC/DoD
- [x] (P0) t01–t07 README AC/DoD checkboxes `[x]` matching corresponding `acceptance-verification-*.md`.
- [x] (P0) Code Facts rewritten to **present** paths (no «absent» for files that exist).
- [x] (P0) Do not change product skeleton; do not reopen story AC; do not invent `src/core/**`.

### Where to change
- `…/task-threads-00-01-t01-pyproject/README.md`
- `…/task-threads-00-01-t02-pyright-requirements/README.md`
- `…/task-threads-00-01-t03-makefile-port/README.md`
- `…/task-threads-00-01-t04-railpack/README.md`
- `…/task-threads-00-01-t05-example-env/README.md`
- `…/task-threads-00-01-t06-readme-gitignore/README.md`
- `…/task-threads-00-01-t07-story-gate/README.md`

### Вне scope
- Backlog/pipeline §Verified current state (t08)
- pytest / product file edits
- pkg-000001 rewrite

### Verification commands
```bash
# P6: after edit, no unchecked AC left in t01–t07 README
rg -n "^- \\[ \\]" doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t0{1,2,3,4,5,6,7}-*/README.md && echo "FAIL leftover [ ]" || echo "t01-t07 AC checked"
rg -n "Target \\*\\*absent\\*\\*" doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t01-pyproject/README.md && echo "FAIL stale absent" || echo "t01 facts present"
```
