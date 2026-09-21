# STORY-THREADS-00-06 — Smoke tests, CI, empty civic/product surface gate

## Meta
- **Key:** `STORY-THREADS-00-06-smoke-tests-ci-empty-surface`
- **Status:** Todo
- **Parent REQ:** [`doge-threads/docs/requirements/00-technical-scaffold.md`](../../../../requirements/00-technical-scaffold.md) §4 Layer 7; AC-THR0-07/09/10/EMPTY
- **Package:** `backlog-stories/00-technical-scaffold/`
- **Skill declared:** `python-pro` @ `.cursor/skills/sources/jeffallan-claude-skills/skills/python-pro/SKILL.md`
- **Depends:** STORY-THREADS-00-04-soa-persistence-migrations, STORY-THREADS-00-05-service-auth-and-outbound-clients
- **Emitted:** 2026-09-21T12:19:10Z

## Зачем
Закрыть REQ0 scaffold Done: offline smoke зелёный, civic modules не просочились, product thread routes не появились.

## Scope
- `tests/conftest.py` fixtures (AppConfig / in_memory factory)
- `tests/smoke/test_health.py` for `/health` `/ready`
- Unit coverage for ServiceTokenAuth / config pilot fail-fast (supports lock **A** from 00-05)
- Makefile `test` green offline
- CI offline pytest workflow pattern (gateway `.github/workflows/` class — Read at implement)
- Verify tree: **no** cluster/intake/geo/schema-packs/promotion modules (AC-THR0-07)
- Verify ASGI: **no** public thread product routes (AC-THR0-10 / EMPTY)

## Вне scope
- `live_integration` against real Supabase (marker reserved only)
- Optional copy of full `docs/runtime-docs/bootstrap-infrastructure/` (REQ OOS)
- Invented protected HTTP path

## Verified current state
| Fact | Path |
|------|------|
| Testing etalon | `doge-complaints-gateway/docs/runtime-docs/bootstrap-infrastructure/06-testing-architecture.md` |
| Gateway CI pattern | `doge-complaints-gateway/.github/workflows/` (Read at implement) |

## Target / AC
- [ ] AC-THR0-09: offline pytest smoke green via `make test` (and/or CI)
- [ ] AC-THR0-07, AC-THR0-10, AC-THR0-EMPTY verified by checklist/tests

## Dependencies
- 00-04, 00-05. Package acceptance gate for REQ0 scaffold Done.
