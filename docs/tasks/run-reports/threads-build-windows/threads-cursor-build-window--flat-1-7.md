---
generated_utc: 2026-09-21T13:35:59Z
builder_project: threads
threads_input_package: doge-threads/docs/tasks/threads-active-packages/pkg-000001-20260921-story-threads-00-01-repo-skeleton.yaml
window_mode: flat_slice
artifact_kind: threads_cursor_build_window
pkg_schema_version: 1
---

# Threads Cursor build window

**Не SSOT.** Очередь и порядок задаёт только YAML-пакет в `threads_input_package`. Не менять список `@…README.md` вручную — перегенерируйте файл командой ниже.

```bash
python3 docs/methodology/Zeya888-builder-queue/cli/builder_resolve_queue.py --project threads --write-build-window --window-flat-start 1 --window-flat-end 7
```

Исполнение: [`threads-story-execution-pipeline.md`](../../threads-story-execution-pipeline.md) + `@.cursor/commands/bullrun-start.md` / `run-task.md`.

## Плоский срез 1–7 (как в --list)
1. `@doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t01-pyproject/README.md`
2. `@doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t02-pyright-requirements/README.md`
3. `@doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t03-makefile-port/README.md`
4. `@doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t04-railpack/README.md`
5. `@doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t05-example-env/README.md`
6. `@doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t06-readme-gitignore/README.md`
7. `@doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/task-threads-00-01-t07-story-gate/README.md`

