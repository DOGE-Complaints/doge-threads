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

Readiness (`/ready`) still does not require these names until STORY-THREADS-01-11 fills `REQUIRED_READINESS_TABLES`.
