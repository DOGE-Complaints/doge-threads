# STORY-THREADS-00-03 — FastAPI /health /ready + DI shell

## Meta
- **Key:** `STORY-THREADS-00-03-fastapi-health-ready-di`
- **Status:** Todo
- **Parent REQ:** [`doge-threads/docs/requirements/00-technical-scaffold.md`](../../../../requirements/00-technical-scaffold.md) §4 Layers 1–2; AC-THR0-01, EMPTY
- **Package:** `backlog-stories/00-technical-scaffold/`
- **Skill declared:** `python-pro` @ `.cursor/skills/sources/jeffallan-claude-skills/skills/python-pro/SKILL.md`
- **Depends:** STORY-THREADS-00-02-config-and-bootstrap
- **Emitted:** 2026-09-21T12:19:10Z

## Зачем
Поднятие HTTP-транспорта с пустой product surface: только health/ready, DI-контейнер готов принимать auth/clients/persistence в следующих stories.

## Scope
- `asgi_app.py`: lifespan, CORS, exception middleware; routes **only** `/health`, `/ready`
- `handlers.py`: health + readiness only
- `envelope.py` error envelope
- `dependencies.py`: `ApiDependencies` + `build_api_dependencies()` + `@lru_cache` (stubs OK)
- `make dev` serves app on PORT (default 8001)

## Вне scope
- Product thread paths (AC-THR0-10 / EMPTY)
- Full auth middleware (00-05); persistence providers (00-04)
- Invented protected HTTP path (operator lock **A**)

## Verified current state
| Fact | Path |
|------|------|
| ASGI etalon | `doge-complaints-gateway/src/core/api/asgi_app.py` |
| No threads ASGI | absent under `doge-threads/src/` |

## Target / AC
- [ ] AC-THR0-01: `make dev` → `/health` and `/ready`
- [ ] AC-THR0-EMPTY / AC-THR0-10: no public thread product routes
- [ ] `in_memory` config can construct app without Supabase (partial AC-THR0-03)

## Точки в коде (target)
- `doge-threads/src/core/api/{asgi_app,handlers,envelope,dependencies}.py`

## Dependencies
- 00-02. Blocks 00-04, 00-05.
