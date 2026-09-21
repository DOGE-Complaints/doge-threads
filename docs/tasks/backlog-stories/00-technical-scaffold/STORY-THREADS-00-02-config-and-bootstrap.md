# STORY-THREADS-00-02 — Config (env_file + slim AppConfig) + bootstrap/logging

## Meta
- **Key:** `STORY-THREADS-00-02-config-and-bootstrap`
- **Status:** Todo
- **Parent REQ:** [`doge-threads/docs/requirements/00-technical-scaffold.md`](../../../../requirements/00-technical-scaffold.md) §4 Layer 3, §5, §6.2
- **Package:** `backlog-stories/00-technical-scaffold/`
- **Skill declared:** `python-pro` @ `.cursor/skills/sources/jeffallan-claude-skills/skills/python-pro/SKILL.md`
- **Depends:** STORY-THREADS-00-01-repo-skeleton
- **Emitted:** 2026-09-21T12:19:10Z

## Зачем
Конфиг как у gateway: pure env mapping, без `python-dotenv` / pydantic-settings. В `pilot` без `SERVICE_API_TOKEN` сервис не должен стартовать.

## Scope
- Copy `env_file.py` **verbatim** from gateway
- Slim `AppConfig` / `ENV_SCHEMA` / `load_config_from_env` — fields for REQ §5 only; omit cluster / NODE_SCHEMA / civic-only
- `APP_PROFILE=pilot` without `SERVICE_API_TOKEN` → fail-fast `ConfigError` (AC-THR0-AUTH config half; operator lock **A**)
- `logging_setup.py`, `bootstrap.py` patterns from gateway

## Вне scope
- HTTP routes; DI wiring of clients; JWT validation; invented protected HTTP path

## Verified current state
| Fact | Path |
|------|------|
| Config etalon | `doge-complaints-gateway/src/core/config/schema.py`, `env_file.py` |
| Pilot token fail-fast | gateway `schema.py` SERVICE_API_TOKEN policy |

## Target / AC
- [ ] AC-THR0-02: AppConfig from env via env_file + schema
- [ ] No pydantic-settings / python-dotenv library
- [ ] Pilot missing `SERVICE_API_TOKEN` fails at config load (AC-THR0-AUTH)

## Точки в коде (target)
- `doge-threads/src/core/config/env_file.py`, `schema.py`
- `doge-threads/src/core/bootstrap.py`, `logging_setup.py`

## Dependencies
- 00-01. Blocks 00-03.
