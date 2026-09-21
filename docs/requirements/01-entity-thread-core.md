# 01. Entity threads — core social layer (shell; no invented API)

Parent: docs/requirements backlog/REQ7-DOGEstonia-Threads-Entity-Social-Governance.md §0, §1 shell, §2.2, §3, §5.1–5.5, §8–§10, T-REQ7-01, T-REQ7-09, D1, D11–D13, D19–D26, D29–D32  
Parent-id: doge-threads-entity-social-governance  
Siblings: doge-threads/docs/requirements/00-technical-scaffold.md (depends-on: implement scaffold before domain stories); doge-complaints-gateway/docs/requirements/52-issue-thread-context-and-node-verification.md (contract: pull — threads asks the gateway for Issue ThreadContext; route and fields still unnamed); spa-app/docs/requirements/17-issue-thread-feed-ux-and-reactions.md (contract: TBD-question — spa renders the dashboard feed; client operations still unnamed); doge-identity-service/docs/requirements/21-verification-boolean-and-audit.md (contract: threads reads the user’s **verified boolean** only; route still unnamed)  
Status: Draft — awaiting PA.2 (shell scope 2026-09-21; Part A locks applied)  
Related algorithms parent: docs/requirements backlog/REQ8-DOGEstonia-Threads-Metrics-Voice-Governance.md (not this child’s AC)  

Дата: 2026-09-21  
Проект: doge-threads  
Фокус: shell — дерево + реакции + вложения. **Без** HTTP path/body. Голоса / дрейф / санкции / метрики → **REQ8**

---

## 1) Goal

Зафиксировать обязанности `doge-threads` как отдельного сервиса ноды для **shell**: дерево комментариев у внешней сущности, хранение меток `reactions.v1`, ссылки на вложения. Не проектировать API. Не требовать кривую веса, scoring дрейфа, sanction signals или emit кабинетных метрик в этом Draft.

## 2) Scope / Out of scope

### In scope (shell)

- Thread keyed by node + entity type + entity id (parent §5.1). Civic first entity is Issue; threads does not own Issues.
- Comment is not a Story and does not by itself change clustering (D1).
- Nested tree; max depth is a node setting (D13).
- Reactions: catalog `reactions.v1` (parent §8 and `docs/requirements backlog/DOGEstonia — Threads — Emotional reactions.md`). Enable/disable and `max_reactions_per_actor` are node settings. Store marks; `agree`⊥`disagree`; layers per §8. **Do not require voice-weight curve** (REQ8).
- Attachments in shell as references (D20). Blob transport remains Open (parent §10, §15). **Platform legal media floor** (parent §9): node cannot disable CSAM / catastrophic-media protection; this service must honour that floor when accepting attachment refs (scanner vendor Open).
- Pull ThreadContext from entity provider (D29). No Story bodies (D19).
- Write path reads **verified boolean** only (D4).

### Out of scope (this child / shell)

- Participant votes (D10) — **REQ8**.
- Sanction **signals** and story-create ban — **REQ8** (gateway enforce also REQ8).
- Raw social metric events for cabinet — **REQ8** (cabinet left as-is).
- Voice-weight consumer / overlap input API — **REQ8**.
- Drift soft→hard scoring engine — **REQ8**.
- Comment **rate limits** and near-duplicate warnings — not shell (parent D32); observe freely.
- Issue projection, clustering, Story intake.
- Deciding what “verified” means; running phone/eID.
- spa layout/copy; Pack Builder; Landing.
- Inventing routes, JSON field names, or DB tables.

## 3) Verified current state

| Fact | Path |
|------|------|
| Repo has no application source | `doge-threads/` listing: `LICENSE`, `docs/tasks/` only; no `src/` |
| Backlog empty | `doge-threads/docs/tasks/backlog-stories/INDEX.md` line 8: “No stories authored yet” |
| Reaction catalog Accepted | `docs/requirements backlog/DOGEstonia — Threads — Emotional reactions.md` |
| Gateway Issues exist; comment entity not found | `doge-complaints-gateway/src/core/api/asgi_app.py:503-556` |

Unknown: process host, datastore, and the wire between this service and gateway/identity/spa.

## 4) Target behavior

1. A thread attaches to an external entity. Creating a comment does not create or mutate a Story or a cluster.
2. Writers must hold the **verified boolean**. This service reads that boolean only.
3. This service **pulls** ThreadContext from the entity provider (D29). Civic = gateway. No Story text. Route unnamed.
4. Node settings control depth and reaction enablement. No appointed moderators.
5. A comment can carry attachment references. Bytes live elsewhere until transport is chosen. Platform legal media floor (parent §9) cannot be disabled by the node.
6. Reaction marks are stored per `reactions.v1`. Weighting, votes, hold/shadow, sanctions, metric emit, rate limits / near-dup are **not** shell targets (D32 / REQ8).

## 5) Acceptance criteria

1. AC-THR-01: This Draft does not mandate a new HTTP path or payload schema.
2. AC-THR-02: Non-goals match parent §2.2: no Story intake, no clustering, no identity verification implementation.
3. AC-THR-03: Reaction **mark** rules cite `reactions.v1` and parent §8 (layers, root vs comments, `agree`⊥`disagree`) without renaming `reaction_id`. Voice-weight application is **not** required.
4. AC-THR-04: Story bodies are forbidden; value-source linkage is opaque ids only (D19).
5. AC-THR-05: ThreadContext is obtained by pull from the entity provider (civic: gateway). Route unnamed (D29).
6. AC-THR-06: The write check reads the verified boolean and nothing about method (D4).
7. AC-THR-07: This Draft does **not** claim sanction signals, cabinet metric emit, vote storage, or drift scoring as shell duties (parent §0 / D31).
8. AC-THR-08: Attachment acceptance honours the platform legal media floor (parent §9 / AC-REQ7-13): a node cannot disable CSAM or equivalent catastrophic-media protection. Scanner vendor Open.
9. AC-THR-09: This Draft does **not** require comment rate limits or near-duplicate warnings (parent D32).

## 6) Open questions

- Route by which this service pulls ThreadContext and reads the verified boolean.
- Where attachment bytes live (parent §15).
- REQ8 timing for voice/drift/sanction/votes/metrics (out of this Draft).

## 7) Dependencies

- **REQ0** [`00-technical-scaffold.md`](./00-technical-scaffold.md) — implement technical scaffold before domain stories for this REQ.
- Parent §0 / D31 shell lock.
- Gateway 52 for Issue ThreadContext pull and pack verification policy **+** shell knobs / Topic-guarded defaults.
- Identity 21 for the verified boolean.
- spa 17 for feed UI of stored comments/reactions.
- **REQ8** [`docs/requirements backlog/REQ8-DOGEstonia-Threads-Metrics-Voice-Governance.md`](../../../docs/requirements%20backlog/REQ8-DOGEstonia-Threads-Metrics-Voice-Governance.md) for votes, sanctions, voice, drift, metrics.
