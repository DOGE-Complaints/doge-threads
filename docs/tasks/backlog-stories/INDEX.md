# Threads backlog stories — INDEX

**Профиль:** `threads` · **Focus:** `doge-threads/`  
**Bullrun:** [bullrun-launch-index.md](../bullrun-launch-index.md)  
**Dashboard:** [threads-mvp-dashboard.md](../threads-mvp-dashboard.md)  
**Updated:** 2026-09-21T13:45:55Z

## Packages

| Package | Progress | Notes |
|---------|----------|-------|
| [00-technical-scaffold](00-technical-scaffold/INDEX.md) | 1/6 Done | REQ0 FastAPI scaffold · order `01→02→03→04∥05→06` |

## Stories (flat)

| Status | Key | Package |
|--------|-----|---------|
| Done | [STORY-THREADS-00-01-repo-skeleton](00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md) | 00-technical-scaffold |
| Todo | [STORY-THREADS-00-02-config-and-bootstrap](00-technical-scaffold/STORY-THREADS-00-02-config-and-bootstrap.md) | 00-technical-scaffold |
| Todo | [STORY-THREADS-00-03-fastapi-health-ready-di](00-technical-scaffold/STORY-THREADS-00-03-fastapi-health-ready-di.md) | 00-technical-scaffold |
| Todo | [STORY-THREADS-00-04-soa-persistence-migrations](00-technical-scaffold/STORY-THREADS-00-04-soa-persistence-migrations.md) | 00-technical-scaffold |
| Todo | [STORY-THREADS-00-05-service-auth-and-outbound-clients](00-technical-scaffold/STORY-THREADS-00-05-service-auth-and-outbound-clients.md) | 00-technical-scaffold |
| Todo | [STORY-THREADS-00-06-smoke-tests-ci-empty-surface](00-technical-scaffold/STORY-THREADS-00-06-smoke-tests-ci-empty-surface.md) | 00-technical-scaffold |

## Fix / build order

1. Foundation / scaffold before feature work: `00-01 → 00-02 → 00-03 → 00-04 ∥ 00-05 → 00-06`.
2. Do not invent AC — only from authored backlog / REQ.
3. Product shell (`01-entity-thread-core`) after REQ0 scaffold Done.
