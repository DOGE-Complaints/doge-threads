## Task workspace — `task-threads-00-01-t06-readme-gitignore`

- Story: [`../STORY-THREADS-00-01-repo-skeleton.md`](../STORY-THREADS-00-01-repo-skeleton.md)
- Decision Ref: backlog STORY-THREADS-00-01 Scope bullet 6; REQ0 §4 Layer 0 `README.md` / `.gitignore`
- Skill declared: `python-pro`

---
**Приоритет:** P0  
**Сложность:** S  
**Статус:** done  
**Wave:** `pkg-000001`  
**Materialized:** 2026-09-21T13:33:54Z  
---

## Task: implement — short README.md + .gitignore (gateway class)

### Purpose
Добавить короткий repo `README.md` (threads shell service) и `.gitignore` класса gateway. README documents default local port 8001.

### Code Facts
1. Present: `doge-threads/README.md` — short shell mission; default local port **8001**.
2. Present: `doge-threads/.gitignore` — `.venv`, `.env`, caches; no civic pack trees.
3. Etalon exists: `doge-complaints-gateway/README.md`, `doge-complaints-gateway/.gitignore`.
4. Story Scope (verbatim): short `README.md`, `.gitignore` (gateway class).
5. Story AC: Default local port documented as 8001.

### Gap
Closed — repo README and `.gitignore` exist.

### AC/DoD
- [x] (P0) `doge-threads/README.md` exists (short mission / threads shell).
- [x] (P0) Default local port **8001** documented in README.
- [x] (P0) `doge-threads/.gitignore` exists (gateway class: venv, `.env`, caches — no invent of civic pack trees unless etalon has them).

### Where to change
- `doge-threads/README.md` (created at P3)
- `doge-threads/.gitignore` (created at P3)

### Вне scope
- Full `docs/runtime-docs/bootstrap-infrastructure/` mirror
- CI workflow (00-06)
- `src/core/**`

### Verification commands
```bash
test ! -f doge-threads/README.md && echo "pre: no repo README"
# after P3:
grep -n '8001' doge-threads/README.md
test -f doge-threads/.gitignore
```
