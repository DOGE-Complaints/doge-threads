# Threads migrations (shared Supabase project)

Apply this folder to the **same** Supabase project as the node (`SUPABASE_URL` / service role already on threads `AppConfig`).

Do **not** create a second database or a second project.

## Ownership

Shell DDL is owned here. Tables in `public`:

- `thread_threads`
- `thread_comments`
- `thread_reaction_marks`
- `thread_attachment_refs`

Prefix `thread_`. Civic / Story tables stay in the gateway repo.

## This story

`202609220919_threads_01_08_shell_tables.sql` — four `thread_*` tables from domain fields + `created_at`; RLS + `service_role` all (gateway class).

## Prod ops (STORY-THREADS-01-11)

Apply this folder to the shared node project **before** setting `DB_BACKEND=supabase` in production. `/ready` fail-closes if any of the four `thread_*` names is missing (`REQUIRED_READINESS_TABLES`). Process restart does not wipe PostgREST-backed rows. `DB_BACKEND=in_memory` stays for offline proofs. Live project is not required for default CI.
