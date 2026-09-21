# P4 Audit — STORY-THREADS-00-01-repo-skeleton

| Field | Value |
|-------|-------|
| **Date** | 2026-09-21 |
| **Mode** | `input_mode=backlog_story` (threads-operator-contract §6) |
| **builder_project** | `threads` (alias ≠ folder; focus `doge-threads/`) |
| **$bullrun** | `doge-threads/docs/tasks/bullrun-launch-index.md` |
| **$story** | `STORY-THREADS-00-01-repo-skeleton` |
| **$storyFile** (AC SSOT) | `doge-threads/docs/tasks/backlog-stories/00-technical-scaffold/STORY-THREADS-00-01-repo-skeleton.md` |
| **Pipeline story** | `doge-threads/docs/tasks/epics/EPIC-THREADS-00-technical-scaffold/stories/STORY-THREADS-00-01-repo-skeleton/STORY-THREADS-00-01-repo-skeleton.md` |
| **Gate** | `…/story-acceptance-gate-STORY-THREADS-00-01.md` Result PASS `2026-09-21T13:37:36Z` |
| **Method** | Read/Glob only vs `doge-threads/` product files + etalon `doge-complaints-gateway/` equivalents; no product patches; no live pytest/`--verify` this pass |
| **Thinking** | `.cursor/rules/analysis.mdc` · workflow §P4 · contract §6 |
| **hasUxPipeline** | `false` — visual/UI-0..UI-3 audit skipped |

## Verdict

| Axis | Result |
|------|--------|
| **Story AC (backlog Target / AC, 4 items)** | **PASS** — все 4 пункта подтверждены файлами на диске |
| **Scope (repo skeleton only)** | **PASS** — Layer 0 артефакты есть; `src/` и `.github/` отсутствуют |
| **Bullrun story/task Done labels** | **Согласованы** с pipeline t01–t07 + gate PASS |
| **OPEN product gaps (actionable)** | **0** |
| **Info docs-drift (не блокируют AC Done)** | **2** (G-01, G-02) — disposition в P5, не в этом отчёте |
| **Live verify this pass** | **Unknown** (команды не запускались); gate artifact claims live PASS @ `2026-09-21T13:37:36Z` |
| **Nested git** | `doge-threads/.git` exists; `HEAD` → `refs/heads/dev` |

---

## Bullrun touchpoints (статусы в отчёте — product index не переписывался)

Источник строк: `$bullrun` §Актуальная точка + §STORY-THREADS-00-01 task table.

| ID | Path / label | Bullrun claim | P4 fact status |
|----|--------------|---------------|----------------|
| Story | STORY-THREADS-00-01-repo-skeleton | Done (P3) | **Confirmed Done** — 4 backlog AC PASS (matrix below) |
| t01 | `task-threads-00-01-t01-pyproject` | Done | **Confirmed** — `doge-threads/pyproject.toml` |
| t02 | `task-threads-00-01-t02-pyright-requirements` | Done | **Confirmed** — `pyrightconfig.json` + `requirements.txt` |
| t03 | `task-threads-00-01-t03-makefile-port` | Done | **Confirmed** — `Makefile` serve/dev/check-env/test, `PORT:-8001` |
| t04 | `task-threads-00-01-t04-railpack` | Done | **Confirmed** — `railpack.json` AC-THR0-08 |
| t05 | `task-threads-00-01-t05-example-env` | Done | **Confirmed** — `example.env` REQ §5 keys, empty values |
| t06 | `task-threads-00-01-t06-readme-gitignore` | Done | **Confirmed** — `README.md` + `.gitignore` |
| t07 | `task-threads-00-01-t07-story-gate` | Done | **Confirmed artifact** — gate PASS + `acceptance-verification-task-threads-00-01-t07-story-gate.md` |
| Epic | EPIC-THREADS-00-technical-scaffold | 00-01 Done; 00-02…06 Todo | **Unchanged** — siblings backlog only (out of this audit) |

**Index recommendation (do not apply in P4):** в `$bullrun` §Актуальная точка добавить строку на этот отчёт (`doge-threads/docs/analysis/p4-audit-STORY-THREADS-00-01-repo-skeleton-20260921.md`); Status «Next» оставить оператору (P5 если нужен disposition Info, иначе P1.3 на 00-02).

---

## AC matrix (backlog `$storyFile` Target / AC)

| # | AC (verbatim) | Status | Evidence (paths) |
|---|----------------|--------|------------------|
| 1 | Artifacts from REQ Layer 0 table exist under `doge-threads/` | **PASS** (CI excepted — story Вне scope / 00-06) | Present: `doge-threads/pyproject.toml`, `pyrightconfig.json`, `requirements.txt`, `Makefile`, `railpack.json`, `example.env`, `README.md`, `.gitignore`. Absent (in scope to remain absent): `doge-threads/src/` (Glob: path does not exist), `doge-threads/.github/` (Glob: path does not exist). REQ Layer 0 CI `.github/workflows/test-offline.yml` = 00-06, not this story. |
| 2 | `railpack.json` startCommand matches uvicorn pattern (AC-THR0-08) | **PASS** | `doge-threads/railpack.json` `deploy.startCommand` = `python -m uvicorn --app-dir src core.api.asgi_app:app --host 0.0.0.0 --port ${PORT:-8001}`. Etalon: `doge-complaints-gateway/railpack.json` same uvicorn pattern, port `${PORT:-8000}`. |
| 3 | Default local port documented as 8001 | **PASS** | `doge-threads/Makefile` L3 comment + `$${PORT:-8001}` in `serve`/`dev`/`check-env`; `doge-threads/README.md` L3; `doge-threads/example.env` L18–19 comment + empty `PORT=`. |
| 4 | `example.env` lists REQ §5 keys without inventing extra civic knobs | **PASS** | `doge-threads/example.env`: `APP_PROFILE`, `DB_BACKEND`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE`, `LOG_LEVEL`, `LOG_DEBUG_DIR`, `SERVICE_API_TOKEN`, `IDENTITY_BASE_URL`, `GATEWAY_BASE_URL`, `PORT` — all empty. No `CLUSTER_*` / `NODE_SCHEMA` / schema-packs / intake secrets (Grep: civic terms only in docs + one comment line in `example.env`). |

### Scope extras (not numbered AC, verified)

| Scope item | Status | Evidence |
|------------|--------|----------|
| `pyproject.toml` name `doge-threads`, `where=["src"]`, Python ≥3.11, marker `live_integration` | **PASS** | `doge-threads/pyproject.toml` L6, L10, L24–25, L32–34 |
| `pyrightconfig.json` gateway class | **PASS** (adapted) | `doge-threads/pyrightconfig.json`: `pythonVersion` 3.11, include/extraPaths `src`/`tests`, venv `.venv`. Etalon `doge-complaints-gateway/pyrightconfig.json` additionally has `scripts` + `executionEnvironments` — threads has no `scripts/` (Glob of product tree). |
| trimmed `requirements.txt` fastapi/uvicorn/httpx; no cluster/geo/schema-packs | **PASS** | `doge-threads/requirements.txt` three lines only. Etalon `doge-complaints-gateway/requirements.txt` also has `psycopg`, `jsonschema` — omitted here. |
| Makefile `serve` / `dev` / `check-env` / `test` | **PASS** | `doge-threads/Makefile` `.PHONY` L1; targets L6/L11/L16/L27. `test` empty-safe until 00-06 (L27–28) — matches t03 DoD. |
| short README + `.gitignore` gateway class | **PASS** | `doge-threads/README.md` (shell + port 8001). `doge-threads/.gitignore`: `.venv`, `.env`, caches — no civic pack trees. Etalon `doge-complaints-gateway/.gitignore` also ignores `docs/analysis/*` and `schema-packs/uus_veerenni_civic/` — not required for threads class. |
| Out of scope: `src/core`, CI, civic modules | **PASS** (absent) | No `src/`; no `.github/`; no product civic modules. |

---

## Gaps

**Actionable product gaps: none.** Story AC / Scope закрыты фактами на диске.

| ID | Severity | Evidence path | Finding | How to close (findings only — no implement) |
|----|----------|---------------|---------|---------------------------------------------|
| **G-01** | **Info** | `$storyFile` L29–33; pipeline story L34–38 | `Verified current state` still says `doge-threads/` = LICENSE + docs only. Disk now also has Layer 0 skeleton files listed in AC matrix. `No src/` remains true. | Sync verified-state table to current files; keep `No src/` until 00-02+. Docs only. |
| **G-02** | **Info** | `…/task-threads-00-01-t01-pyproject/README.md` … `t07-…/README.md` AC/DoD still `[ ]`; Code Facts still «absent» | Task README status = `done` and acceptance-verification files = PASS, but README AC checkboxes and pre-P3 «absent» facts were not refreshed. | Check AC boxes to match `acceptance-verification-*.md`; rewrite Code Facts to present paths. Docs only; not a product AC fail. |

### Non-gaps / out of DoD this wave

| Topic | Note |
|-------|------|
| CI `.github/workflows/test-offline.yml` | REQ Layer 0 row; story Вне scope → `STORY-THREADS-00-06` |
| `src/core/**` / asgi_app | 00-02+; railpack/Makefile only *name* the future module |
| `make serve`/`dev` runtime (no asgi yet) | Expected; story does not require a running app |
| Live `make test` / `--verify` this P4 pass | **Unknown**; not re-run. Gate + per-task acceptance claim PASS @ `2026-09-21T13:37:36Z` |
| pyrightconfig not byte-identical to gateway | Adaptation (no `scripts/`); t02 DoD = gateway class / 3.11 |
| Makefile uses `python3` not `.venv/bin/python` | Story/AC do not require venv interpreter |
| Nested `doge-threads/.git` vs workspace root git | Confirmed nested repo on `dev`; do not confuse with DOGEstonia root |

---

## Regressions

Не обнаружены относительно backlog AC и etalon pattern (uvicorn `--app-dir src core.api.asgi_app:app`; trimmed deps; PORT 8001 ≠ gateway 8000).

---

## P5 / next

Не стартовать P5 из этого отчёта. 0 OPEN product gaps. G-01/G-02 — Info docs-drift; disposition только по явному fence P5 от OP.
