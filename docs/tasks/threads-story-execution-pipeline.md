# Threads — Story execution pipeline

> **Профиль Builder Queue:** `threads`  
> **Операторский маршрут:** [`docs/methodology/Zeya888-builder-queue/core/workflow.md`](../../../docs/methodology/Zeya888-builder-queue/core/workflow.md)  
> **Runtime plan:** [`.cursor/plans/Threads_builder.plan.md`](../../../.cursor/plans/Threads_builder.plan.md)

**Alias ≠ folder:** `threads` → `doge-threads/`.

## SSOT

| Слой | Источник |
|------|----------|
| Builder Queue statuses | [`bullrun-launch-index.md`](bullrun-launch-index.md) |
| Очередь исполнения | immutable `threads-active-packages/pkg-*.yaml` |
| Backlog | [`backlog-stories/INDEX.md`](backlog-stories/INDEX.md) |
| Operator contract | [`threads-operator-contract.md`](../../../docs/methodology/Zeya888-builder-queue/contracts/threads-operator-contract.md) |
| Tests | `cd doge-threads && python3 -m pytest -q` (`profiles.yaml` → `test_command`; Phase 0 fails until REQ0 scaffold) |

## Skill routing

| Зона | Skill |
|------|-------|
| Python 3.11 + FastAPI + uvicorn + httpx | `python-pro` |
| Task README override | as declared in README |

## Перед batch-run (обязательно)

1. [`bullrun-launch-index.md`](bullrun-launch-index.md) §«Актуальная точка».
2. [`threads-active-package.current.yaml`](threads-active-package.current.yaml) → `package_file`.
3. `python3 docs/methodology/Zeya888-builder-queue/cli/builder_resolve_queue.py --project threads --verify`
4. Epic/story without materialized task queue → **P1.1** / **P1.3**, not P3 Execute.
5. One `input_mode` per session (contract §4).

## Gate: Story AC

After last task README in story — AC from materialized story or backlog `STORY-THREADS-*`.

## Gate: Epic AC

After all stories in epic — Goal/AC in epic file.

## Phases

Follow [workflow.md](../../../docs/methodology/Zeya888-builder-queue/core/workflow.md) **P1–P8**. Fixed plan: @attach `Threads_builder.plan.md` — **не** Build на файле.
