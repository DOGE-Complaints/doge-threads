# 00-technical-scaffold — INDEX

> **Пакет:** REQ0 Technical scaffold (FastAPI service bootstrap)  
> **Parent REQ:** [`../../../requirements/00-technical-scaffold.md`](../../../requirements/00-technical-scaffold.md)  
> **Dashboard:** [`../../threads-mvp-dashboard.md`](../../threads-mvp-dashboard.md)  
> **Emitted:** 2026-09-21T12:19:10Z · materialize from REQ→backlog plan (operator «запиши»)  
> **Locks:** Auth probe = **A** (unit/config only, no invented protected HTTP path); migrations = **folder only** (no mandatory placeholder SQL)

## Stories

| Status | Key | Title | Depends |
|--------|-----|-------|---------|
| Done | STORY-THREADS-00-01-repo-skeleton | [Repo skeleton](STORY-THREADS-00-01-repo-skeleton.md) | — |
| Todo | STORY-THREADS-00-02-config-and-bootstrap | [Config + bootstrap](STORY-THREADS-00-02-config-and-bootstrap.md) | 00-01 |
| Todo | STORY-THREADS-00-03-fastapi-health-ready-di | [FastAPI health/ready + DI](STORY-THREADS-00-03-fastapi-health-ready-di.md) | 00-02 |
| Todo | STORY-THREADS-00-04-soa-persistence-migrations | [SOA + persistence + migrations folder](STORY-THREADS-00-04-soa-persistence-migrations.md) | 00-03 |
| Todo | STORY-THREADS-00-05-service-auth-and-outbound-clients | [Service auth + outbound clients](STORY-THREADS-00-05-service-auth-and-outbound-clients.md) | 00-03 |
| Todo | STORY-THREADS-00-06-smoke-tests-ci-empty-surface | [Smoke tests + empty surface](STORY-THREADS-00-06-smoke-tests-ci-empty-surface.md) | 00-04, 00-05 |

## Build order

`01 → 02 → 03 → 04 ∥ 05 → 06`

## Out of package

- Product thread CRUD / reactions / DDL columns → REQ `01` / wire  
- Profile stack lock in `profiles.yaml` → separate methodology dialog (operator)  
- Optional full `docs/runtime-docs/bootstrap-infrastructure/` mirror → later story
