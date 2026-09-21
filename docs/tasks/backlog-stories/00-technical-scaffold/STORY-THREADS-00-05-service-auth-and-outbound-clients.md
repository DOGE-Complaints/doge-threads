# STORY-THREADS-00-05 — ServiceTokenAuth + Identity Me + Gateway clients

## Meta
- **Key:** `STORY-THREADS-00-05-service-auth-and-outbound-clients`
- **Status:** Todo
- **Parent REQ:** [`doge-threads/docs/requirements/00-technical-scaffold.md`](../../../../requirements/00-technical-scaffold.md) §4 Layer 6, §6; AC-THR0-AUTH/OUT/05/06
- **Package:** `backlog-stories/00-technical-scaffold/`
- **Skill declared:** `python-pro` @ `.cursor/skills/sources/jeffallan-claude-skills/skills/python-pro/SKILL.md`
- **Depends:** STORY-THREADS-00-03-fastapi-health-ready-di (DI); config from 00-02
- **Emitted:** 2026-09-21T12:19:10Z
- **Operator lock:** Auth probe = **A** — unit tests of `ServiceTokenAuth` + config fail-fast; **no** invented protected HTTP route

## Зачем
Свой серверный токен на входе; исходящие клиенты к Identity (`/me` etalon) и Gateway (база для будущего ThreadContext pull) — injectable и stubbable.

## Scope
- `security.py`: ServiceTokenAuth for `Authorization: Bearer …` / `X-Service-Token` = threads `SERVICE_API_TOKEN`
- Prove AC-THR0-AUTH via: (1) config fail-fast in pilot (00-02), (2) **unit tests** of token extract/validate — **not** a new public/protected product path
- `/health` remains public
- **No** local JWT validator
- Identity Me client (`IDENTITY_BASE_URL`) injectable; stubbable in tests
- Gateway httpx client (`GATEWAY_BASE_URL`) injectable; stubbable; **no** ThreadContext route mandated
- User-token header **forward** pattern as gateway etalon (header name from etalon Read at implement — do not invent a second scheme)
- Outbound civic calls may attach service token header; shared vs distinct secret = Open (REQ §9)

## Вне scope
- ThreadContext path/body; verified-boolean product write gate (REQ01); JWT parse
- Any invented protected HTTP URL for “401 demo”

## Verified current state
| Fact | Path |
|------|------|
| Service token etalon | `doge-complaints-gateway/src/core/api/security.py` |
| Me client etalon | `doge-complaints-gateway/src/core/identity/me_client.py` |

## Target / AC
- [ ] AC-THR0-AUTH: reject missing/invalid service token under pilot/strict (config + unit tests; lock A)
- [ ] AC-THR0-05 / AC-THR0-06 / AC-THR0-OUT: both clients exist, injectable, tests without live remotes

## Точки в коде (target)
- `doge-threads/src/core/api/security.py`
- `doge-threads/src/core/identity/me_client.py` (or equivalent package path)
- `doge-threads/src/core/gateway/` client module (name at implement; route unnamed)

## Dependencies
- 00-03. Soft-blocks 00-06.
