# task-threads-boot-t00 — Threads Builder Queue profile SSOT

**Status:** Done (methodology bootstrap)  
**Skill declared:** `python-pro`  
**ui_scope:** none

## Goal

Marker task so `--project threads --verify` has 1 path. Does **not** implement product code in `doge-threads/`.

## Scope

- Confirms profile `threads` SSOT exists (`profiles.yaml`, bullrun-launch-index, pipeline, operator contract, `Threads_builder.plan.md`).
- Points operator to next work: author backlog `STORY-THREADS-*` → **P1.3**, or shape via PA + requirement (e.g. parent REQ7 framing).
- Distinguishes alias `threads` from folder `doge-threads/`.

## Out of scope

- Inventing product stories/AC without REQ/backlog evidence.
- P3 product remediation on this marker.
- Cloning remotes or inventing stack/skills.

## Acceptance

- [x] `python3 docs/methodology/Zeya888-builder-queue/cli/builder_resolve_queue.py --project threads --verify` → ok 1 paths
- [ ] Next session: author `STORY-THREADS-*` (or agreed key) → P1.3 (do not re-run this marker as product work)

## Notes

Remote: https://github.com/DOGE-Complaints/doge-threads (`dev`). Stack locked: Python 3.11 + FastAPI + uvicorn + httpx; skill `python-pro` (scaffold lands in REQ0).
