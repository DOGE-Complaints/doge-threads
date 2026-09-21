# Threads migrations (shared Supabase project)

Apply this folder to the **same** Supabase project as the node (`SUPABASE_URL` / service role already on threads `AppConfig`).

Do **not** create a second database or a second project.

## Prefix

Future tables owned here use `thread_` or `thr_`. Civic tables stay in the gateway repo.

## This story

Folder only. No placeholder SQL. Product DDL columns are owned by REQ01.

Readiness (`/ready`) must not require civic tables; thread tables are checked only after they exist.
