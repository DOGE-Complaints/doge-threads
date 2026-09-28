# Public social HTTP — routes & contracts

| Field | Value |
|-------|--------|
| **Parent** | [`00-overview.md`](./00-overview.md) |
| **Stories** | HTTP-02…05 · Close HTTP-06 |
| **Recorded** | 2026-09-23T12:28:24Z |

Semantics (fields, ops) from FE api-req; **path strings** = operator locks N1+K2 (below). W2 = all rows in first Close.

## Routes

| Priority | Method | Path | Handler intent |
|----------|--------|------|----------------|
| P0 | `GET` | `/threads/knobs` | Snapshot `FixedThreadKnobs` (node-level) |
| P0 | `GET` | `/threads/issues/{issue_id}` | `list_comments` + U2 summaries; **no** knobs in body (T1) |
| P0 | `POST` | `/threads/issues/{issue_id}/comments` | `write_comment` (root/reply via `parent_id`) |
| P1 | `PUT` | `/threads/issues/{issue_id}/reactions` | `write_reaction` add/remove |
| P1 | `POST` | `/threads/issues/{issue_id}/attachment-refs` | `write_attachment_ref` (no blob) |

### Superseded FE draft paths (do not implement)

- `/threads/by-issue/...` (any)
- `/threads/by-issue/{id}/knobs`
- Embed `knobs` inside tree `data` as P0 requirement

## Tree success `data` (minimum)

```json
{
  "issue_id": "<string>",
  "comments": [
    {
      "comment_id": "<string>",
      "parent_id": null,
      "depth": 0,
      "body": "<string>",
      "summary_marks": [{"reaction_id": "<string>", "count": 0}],
      "aggregate_count": 0
    }
  ],
  "thread_root_reactions": {
    "summary_marks": [{"reaction_id": "<string>", "count": 0}],
    "aggregate_count": 0
  }
}
```

## Knobs success `data` (minimum)

```json
{
  "max_depth": 8,
  "max_reactions_per_actor": 1,
  "reactions_enable": {},
  "media_allowed_types": []
}
```

Values from domain knobs / compose mapping; **U1**: align `max_reactions_per_actor` with FE picker (≥3) at implement.

## Comment / reaction / attach bodies

Unchanged vs FE api-req §3 / §5 / §6 (field semantics). Only path prefix `…/issues/…`.

## ThreadKey fill

- `entity_id` ← path `issue_id`
- `entity_type` ← `"Issue"`
- `node` ← `DOGESTONIA_SCHEMA_ID` (see [`03-node-env-and-threadkey.md`](./03-node-env-and-threadkey.md))
