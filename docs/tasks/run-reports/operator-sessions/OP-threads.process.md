# OP-threads.process.md — overnight subagent SSOT

**Working plan:** [`.cursor/plans/OP-threads-00-technical-scaffold-20260921.plan.md`](../../../../../.cursor/plans/OP-threads-00-technical-scaffold-20260921.plan.md)  
**Session:** [`OP-threads.session.yaml`](./OP-threads.session.yaml)  
**Wave:** [`../operator-waves/wave-20260921-00-technical-scaffold.md`](../operator-waves/wave-20260921-00-technical-scaffold.md)  
**Updated:** 2026-09-21T13:28:57Z  
**NO agent ids in this file.**

## Model

- OP orchestrates only; **two** Task subagents (Builder + Validator); verbatim fences; no UI paste.
- Claims: Read/Glob only ([analysis.mdc](../../../../../.cursor/rules/analysis.mdc)).
- OP does not write product code, invent AC, or push.
- Titles: `OP-threads` / `BLD-threads` / `VAL-threads`. Alias `threads` → `doge-threads/`.

## Overnight non-stop

| Правило | Поведение |
|---------|-----------|
| Стоп | только `стоп` / `stop` / `pause` / `halt` |
| P1.3a→P1.3b / P5a→P5b | OP auto-approve (overnight) |
| После P8/DONE | сразу следующая QUEUED |
| BLOCKED | факт в wave → очередь дальше |
| P8 | local commits, no push |

## Constants (threads)

| Variable | Value |
|----------|-------|
| `$builderProject` | `threads` |
| `workspace_root` | `/Users/eslinko/Development/DOGEstonia` |
| `$tasksRoot` | `doge-threads/docs/tasks` |
| `$planFile` | `.cursor/plans/Threads_builder.plan.md` |
| `$pipelineDoc` | `doge-threads/docs/tasks/threads-story-execution-pipeline.md` |
| `$verifyCmd` | `python3 docs/methodology/Zeya888-builder-queue/cli/builder_resolve_queue.py --project threads --verify` |
| `$backlogIndex` | `doge-threads/docs/tasks/backlog-stories/INDEX.md` |
| contract | `docs/methodology/Zeya888-builder-queue/contracts/threads-operator-contract.md` |
| dashboard | not in contract body; INDEX cites `doge-threads/docs/tasks/threads-mvp-dashboard.md` |
| skill | `python-pro` @ `.cursor/skills/sources/jeffallan-claude-skills/skills/python-pro/SKILL.md` |
| hasUxPipeline | false |
| P1.3 | clean backlog_story; appendix contract §7 |
| t00 | methodology marker — not P3 product |

## Queue

STORY-THREADS-00-01…06 sequential (00-technical-scaffold). See working plan table. Status at start: 6 Todo.

## Plan simulation + ROLE_LOCK

P1.3/P5 = PLAN_DRAFT → auto GATE → PLAN_APPLY. Each Task prompt prepends ROLE_LOCK (orchestrator-builder-reference §4.2 / §5).

### ROLE_LOCK (every phase)

```text
ROLE_LOCK: Execute ONLY the fence below. RETURN_TO_ROOT: paths + ≤5 lines facts. Do not advance phases yourself.
```

### PLAN_DRAFT

```text
SIMULATED_CURSOR_MODE: plan
STEP: PLAN_DRAFT
Allowed writes: ONLY ephemeral .cursor/plans/p1_*_scaffold_*.plan.md OR p5_*_gap_*.plan.md
Forbidden: epics/**/stories/** materialize, task README, pkg-*.yaml, *-active-package.current.yaml,
  bullrun-launch-index.md edits, product source under focus_folder, $planFile body (except reading).
Output: plan file path + mapping preview (no apply).
```

### PLAN_APPLY

```text
SIMULATED_CURSOR_MODE: plan_apply
STEP: PLAN_APPLY
Approved ephemeral plan: <path>
Execute materialize per that plan + original P1.3|P5 fence checklist.
Then --verify / --verify --check-dates as fence requires.
```

## Phase script

0 wave → (0b/0c once if ids missing/dead) → P1.3a/b → P2 shell → P3 → P4 → P5a/b → P6 (skip if TASKED=0) → P7 → P8 → next story.

Skip P1.3 only if pkg/pipeline already on disk (document in wave).
