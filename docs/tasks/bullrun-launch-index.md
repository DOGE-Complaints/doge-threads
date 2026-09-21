# Threads — bullrun launch index (Builder Queue)

**Профиль:** `threads` · **Focus:** `doge-threads/` · **Стек:** Python 3.11 + FastAPI + uvicorn + httpx  
**Pipeline:** [threads-story-execution-pipeline.md](./threads-story-execution-pipeline.md)  
**Active pkg:** [threads-active-package.current.yaml](./threads-active-package.current.yaml) · **pkg-000001** STORY-THREADS-00-01  
**Remote:** https://github.com/DOGE-Complaints/doge-threads (`dev`)  
**Runtime plan:** [Threads_builder.plan.md](../../../.cursor/plans/Threads_builder.plan.md)  
**Contract:** [threads-operator-contract.md](../../../docs/methodology/Zeya888-builder-queue/contracts/threads-operator-contract.md)

**Alias ≠ folder:** `builder_project: threads` → code root `doge-threads/`.

## Актуальная точка

| Поле | Значение |
|------|----------|
| **Active pkg** | `pkg-000001-20260921-story-threads-00-01-repo-skeleton.yaml` (7 paths — t01–t07) |
| **Status** | STORY-THREADS-00-01 **Done**. P6 t08/t09 **Done**. **Next:** P7 from OP. |
| **Story** | `STORY-THREADS-00-01-repo-skeleton` under `EPIC-THREADS-00-technical-scaffold` |
| **Verify** | `python3 docs/methodology/Zeya888-builder-queue/cli/builder_resolve_queue.py --project threads --verify` → ok 7 paths (pkg-000001; t08/t09 via run_mode only) |
| **P4** | [p4-audit-STORY-THREADS-00-01-repo-skeleton-20260921.md](../analysis/p4-audit-STORY-THREADS-00-01-repo-skeleton-20260921.md) |
| **Updated** | 2026-09-21T13:45:55Z |
| **Skill** | `python-pro` |

## Packages

| Pkg | Label | Paths | Status |
|-----|-------|-------|--------|
| [pkg-000000](./threads-active-packages/pkg-000000-20260919-bootstrap.yaml) | bootstrap | 1 (t00) | Done (marker; superseded as active pointer) |
| [pkg-000001](./threads-active-packages/pkg-000001-20260921-story-threads-00-01-repo-skeleton.yaml) | story-threads-00-01-repo-skeleton | 7 | Done (P3) |

## Epics / stories

| Epic | Story | Status | Tasks |
|------|-------|--------|-------|
| [EPIC-THREADS-00-technical-scaffold](./epics/EPIC-THREADS-00-technical-scaffold/EPIC-THREADS-00-technical-scaffold.md) | [STORY-THREADS-00-01-repo-skeleton](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/STORY-THREADS-00-01-repo-skeleton.md) | Done | t01–t09 Done |
| EPIC-THREADS-00-technical-scaffold | STORY-THREADS-00-02…06 | Todo (backlog only) | — |

### STORY-THREADS-00-01 task table

| # | Path | Status |
|---|------|--------|
| t01 | [task-threads-00-01-t01-pyproject](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t01-pyproject/README.md) | Done |
| t02 | [task-threads-00-01-t02-pyright-requirements](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t02-pyright-requirements/README.md) | Done |
| t03 | [task-threads-00-01-t03-makefile-port](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t03-makefile-port/README.md) | Done |
| t04 | [task-threads-00-01-t04-railpack](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t04-railpack/README.md) | Done |
| t05 | [task-threads-00-01-t05-example-env](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t05-example-env/README.md) | Done |
| t06 | [task-threads-00-01-t06-readme-gitignore](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t06-readme-gitignore/README.md) | Done |
| t07 | [task-threads-00-01-t07-story-gate](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t07-story-gate/README.md) | Done |
| t08 | [task-threads-00-01-t08-audit-g01-sync-verified-state](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t08-audit-g01-sync-verified-state/README.md) | Done (P6 G-01) |
| t09 | [task-threads-00-01-t09-audit-g02-refresh-task-readme-facts](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t09-audit-g02-refresh-task-readme-facts/README.md) | Done (P6 G-02) |

**Gate:** [story-acceptance-gate-STORY-THREADS-00-01.md](./epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/story-acceptance-gate-STORY-THREADS-00-01.md) PASS `2026-09-21T13:37:36Z`  
**Run summary:** [run-summary-20260921-1337.md](./run-reports/run-summary-20260921-1337.md)  
**P5 disposition:** G-01 TASKED t08 · G-02 TASKED t09 · CLOSED 0 · WAIVED 0 · product OPEN 0.  
**P6:** t08/t09 PASS `2026-09-21T13:45:55Z` · [run-summary-20260921-1345.md](./run-reports/run-summary-20260921-1345.md) · pkg-000001 unchanged.

## Input package (run metadata)

Column / field: `threads_input_package`.
