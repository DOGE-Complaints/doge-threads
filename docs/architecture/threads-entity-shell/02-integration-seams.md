# Integration seams — Gateway, Identity, Spa

| Field | Value |
|-------|--------|
| **Parent** | [`00-overview.md`](./00-overview.md) |
| **REQ** | [`../../requirements/01-entity-thread-core.md`](../../requirements/01-entity-thread-core.md) AC-THR-05/06 |
| **Siblings** | Gateway [`52-issue-thread-context-and-node-verification.md`](../../../../doge-complaints-gateway/docs/requirements/52-issue-thread-context-and-node-verification.md); Identity [`21-verification-boolean-and-audit.md`](../../../../doge-identity-service/docs/requirements/21-verification-boolean-and-audit.md); Spa [`17-issue-thread-feed-ux-and-reactions.md`](../../../../spa-app/docs/requirements/17-issue-thread-feed-ux-and-reactions.md) |
| **Recorded** | 2026-09-21T18:58:51Z · **Wire sync** 2026-09-21T21:10:54Z (`identity_verified` on `/me` Done) |
| **Prior arch files (identity 3a / gateway 3b)** | Unknown on disk — decisions taken from child REQs + this interview |

---

## 1) Gateway — ThreadContext pull (+ shell knobs)

**Product rule (D29):** threads **pulls**; gateway does not push. No Story bodies.

**Operator lock A:** logical ThreadContext for civic Issues includes:

1. Issue adapter capabilities (parent §5.3 class: title, discussion taxonomy, binding mode, opaque story ids, safety/escalation pointers — exact fields Open).
2. **Shell knobs** materialized in the active pack on gateway (sibling `52`): `max_depth`, per-reaction enables, `max_reactions_per_actor`, Topic-guarded presentation defaults, media-type allowlist within legal floors.

Threads does **not** load schema-packs itself (REQ0 OOS). Knobs are consumed only via this pull.

**HTTP route / JSON keys:** unnamed (Open). Scaffold client: `doge-threads/src/core/gateway/client.py` (transport stub; product semantics not yet implemented).

**Compose-pull unwrap (H6 / `_as_gateway_body`):** `pull_thread_context.py` accepts a **bare** JSON object or an Ops success envelope `{data, trace_id}` when `data` is a Mapping — no new envelope fields. Used for Issue get (`GET /node/issues/{issue_id}`) and pack shell (`GET /node/shell-settings`). After unwrap: `assert_no_story_narrative`; issue → `parse_issue_projection`; pack → require `pack_shell_settings`. No debug I/O on this path.

---

## 2) Identity — verified boolean

**Product rule (D4 / AC-THR-06):** every write path reads method-opaque **verified boolean** only.

**Wire (sibling `21` / EPIC-IDS-15 Done):** consumers read **`identity_verified`** on existing **`GET /me`** — not a new path. SSOT: [TECH-ARCH-threads-verification-boolean](../../../../doge-identity-service/docs/architecture/TECH-ARCH-threads-verification-boolean.md), [API_REFERENCE §6](../../../../doge-identity-service/docs/runtime-docs/api-reference/API_REFERENCE.md), [REQ 21](../../../../doge-identity-service/docs/requirements/21-verification-boolean-and-audit.md). Legacy `phone_verified` may coexist on `/me` / introspect for other gates but **must not** be the sole threads write contract.

**Threads behavior:** fail-closed if Identity unavailable or `identity_verified` false/missing for a write. No local JWT validation (REQ0).

Scaffold client: `doge-threads/src/core/identity/me_client.py`.

---

## 3) Spa — feed consumer

Spa renders Issue thread feed / picker (sibling `17`). Client operations remain TBD-question. This arch does not name spa routes. **Spa O** proceeds after this package is on disk.

---

## 4) Sequence dependency

```text
REQ0 scaffold (Done) → this tech arch → optional PA.2 on REQ 01
  → backlog stories for domain → wire naming → spa arch/stories
```

Gateway pack materialize of knobs (REQ `52`) and Identity boolean expose (REQ `21`) were **parallel sibling** deliveries; Identity wire **`identity_verified` on `/me`** is **Done** (VB-01…03). Threads write enforce reads that field when product paths land.
