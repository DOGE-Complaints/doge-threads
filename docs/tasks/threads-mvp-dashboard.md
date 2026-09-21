# Threads · scope dashboard

> **Scope-Id:** mvp  
> **Scope:** MVP  
> **SSOT:** [backlog-stories/INDEX.md](backlog-stories/INDEX.md) · [00-technical-scaffold/INDEX.md](backlog-stories/00-technical-scaffold/INDEX.md) · [REQ0](../requirements/00-technical-scaffold.md) · [REQ01](../requirements/01-entity-thread-core.md)  
> **Updated:** 2026-09-21T12:19:10Z  
> **Last change:** Materialize REQ0 package — STORY-THREADS-00-01…06 Todo (auth lock A; migrations folder-only).

## Summary

| Metric | Value |
|--------|-------|
| Backlog packages | 1 |
| Active work items | 6 |
| Done | 0 |
| Scaffolded | 0 |
| Todo | 6 (THREADS-00-01…06) |
| Deferred | 0 |
| **Overall progress (active)** | **0%** `░░░░░░░░░░░░` |

*Active = Todo 00-01…06. Formula: filled = round(12 × 0/6) = 0.*

## By package

| Package | Stories | Done | Scaffolded | Todo | Deferred | Progress |
|---------|---------|------|------------|------|----------|----------|
| [00-technical-scaffold](backlog-stories/00-technical-scaffold/INDEX.md) | 6 | 0 | 0 | 6 | 0 | **0%** |

## Remaining

| Pri | Story | Package | Status | Notes |
|-----|-------|---------|--------|-------|
| 1 | [THREADS-00-01](backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md) | 00-technical-scaffold | Todo | repo skeleton / railpack |
| 2 | [THREADS-00-02](backlog-stories/00-technical-scaffold/STORY-THREADS-00-02-config-and-bootstrap.md) | 00-technical-scaffold | Todo | env_file + AppConfig |
| 3 | [THREADS-00-03](backlog-stories/00-technical-scaffold/STORY-THREADS-00-03-fastapi-health-ready-di.md) | 00-technical-scaffold | Todo | /health /ready + DI |
| 4 | [THREADS-00-04](backlog-stories/00-technical-scaffold/STORY-THREADS-00-04-soa-persistence-migrations.md) | 00-technical-scaffold | Todo | SOA + migrations **folder** |
| 5 | [THREADS-00-05](backlog-stories/00-technical-scaffold/STORY-THREADS-00-05-service-auth-and-outbound-clients.md) | 00-technical-scaffold | Todo | auth **A** + Me/Gateway clients |
| 6 | [THREADS-00-06](backlog-stories/00-technical-scaffold/STORY-THREADS-00-06-smoke-tests-ci-empty-surface.md) | 00-technical-scaffold | Todo | smoke + empty surface gate |

## §Deferred

| Story | Notes |
|-------|--------|
| — | — |

## §Now

1. **REQ0 scaffold:** `01 → 02 → 03 → 04 ∥ 05 → 06` (optional PA.3 refine → **P1.3** per story).  
2. Parallel (other chat): lock `profiles.yaml` stack/skill to `python-pro` when methodology dialog finishes.  
3. Do **not** P3 product thread routes until REQ0 Done.

## How to refresh

Recount from disk: package INDEX statuses + root backlog INDEX. Optional: `npm run dashboard:aggregate`.
