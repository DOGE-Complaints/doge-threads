## Task workspace — `task-threads-00-01-t03-makefile-port`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: backlog STORY-THREADS-00-01 Scope bullet 3 + AC «Default local port documented as 8001»; REQ0 §4 Layer 0 Makefile
- Skill declared: `python-pro`

---
**Приоритет:** P0  
**Сложность:** S  
**Статус:** done  
**Wave:** `pkg-000001`  
**Materialized:** 2026-09-21T13:33:54Z  
---

## Task: implement — Makefile serve/dev/check-env/test (PORT=8001)

### Purpose
Создать `Makefile` с целями `serve` / `dev` / `check-env` / `test`; default `PORT=8001` (не 8000 gateway).

### Code Facts
1. Present: `doge-threads/Makefile` — targets `serve`, `dev`, `check-env`, `test`; default `PORT:-8001`.
2. Etalon exists: `doge-complaints-gateway/Makefile` — targets `serve`, `dev`, `check-env`; default `PORT:-8000`; **no** `test:` target.
3. REQ0 §4 Layer 7: Makefile `test` required for threads (gateway lacks it).
4. Story Scope (verbatim): `Makefile`: `serve` / `dev` / `check-env` / `test`; default `PORT=8001`.

### Gap
Closed — Makefile exists with PORT 8001.

### AC/DoD
- [x] (P0) `doge-threads/Makefile` has `serve`, `dev`, `check-env`, `test`.
- [x] (P0) Default local port in serve/dev is **8001**.
- [x] (P1) `test` target exists (body may stay empty-safe until 00-06 smoke; do not invent product tests here).

### Where to change
- `doge-threads/Makefile` (created at P3)

### Вне scope
- `src/core/**` / asgi app (00-02+)
- CI workflow body (00-06)
- Product thread routes

### Verification commands
```bash
test ! -f doge-threads/Makefile && echo "pre: absent"
# after P3:
grep -E '^(serve|dev|check-env|test):' doge-threads/Makefile
grep -n '8001' doge-threads/Makefile
```
