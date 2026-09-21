# STORY-THREADS-00-04 — SOA factory + persistence backends + migrations folder

## Meta
- **Key:** `STORY-THREADS-00-04-soa-persistence-migrations`
- **Status:** Todo
- **Parent REQ:** [`doge-threads/docs/requirements/00-technical-scaffold.md`](../../../../requirements/00-technical-scaffold.md) §4 Layers 4–5, §7
- **Package:** `backlog-stories/00-technical-scaffold/`
- **Skill declared:** `python-pro` @ `.cursor/skills/sources/jeffallan-claude-skills/skills/python-pro/SKILL.md`
- **Depends:** STORY-THREADS-00-03-fastapi-health-ready-di
- **Emitted:** 2026-09-21T12:19:10Z
- **Operator lock:** migrations = **folder only** (no mandatory placeholder SQL file)

## Зачем
Подключить те же три backend'а, что у gateway (`in_memory` / `sqlite` / `supabase`), на **общий** Supabase project ноды. Таблицы `thread_*` появятся позже (REQ01); сейчас — способность и папка миграций.

## Scope
- `application/factory.py` Protocol (ThreadServiceFactory — concrete product names TBD in REQ01)
- `infrastructure/providers.py` + `service_factory.py`: `in_memory` | `sqlite` | `supabase`
- PostgREST httpx client pattern; empty thread-focused repo stubs OK
- Create `doge-threads/supabase/migrations/` folder (+ short README of apply-to-shared-project process if helpful)
- **Do not** require placeholder `.sql` for Done
- Prefix convention `thread_` / `thr_`; **no** `CREATE SCHEMA`; **no** invented column lists
- Readiness: do not require civic tables (`stories` / `doge_issues`); thread tables only when they exist later

## Вне scope
- Thread/comment/reaction DDL columns; civic table ownership; second database / second Supabase project

## Verified current state
| Fact | Path |
|------|------|
| Persistence etalon | `doge-complaints-gateway/docs/runtime-docs/bootstrap-infrastructure/04-supabase-persistence.md` |
| Gateway migrations (civic) | `doge-complaints-gateway/supabase/migrations/` — ownership stays gateway |

## Target / AC
- [ ] AC-THR0-03: `DB_BACKEND=in_memory` boots without Supabase
- [ ] AC-THR0-04: supabase backend uses shared credentials; migrations **folder** exists; readiness documented for future thread tables
- [ ] No invented product column lists / no mandatory placeholder SQL

## Dependencies
- 00-03. Soft-blocks 00-06.
