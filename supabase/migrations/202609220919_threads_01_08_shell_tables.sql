-- STORY-THREADS-01-08: shared public shell tables (domain fields + created_at).
-- Apply to the same node Supabase project. No civic / Story tables. No second Postgres.

create table if not exists public.thread_threads (
    node text not null,
    entity_type text not null,
    entity_id text not null,
    created_at timestamptz not null default now(),
    primary key (node, entity_type, entity_id)
);

create table if not exists public.thread_comments (
    comment_id text primary key,
    node text not null,
    entity_type text not null,
    entity_id text not null,
    parent_id text,
    body text not null,
    depth integer not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_thread_comments_thread_key
    on public.thread_comments (node, entity_type, entity_id);

create index if not exists idx_thread_comments_parent_id
    on public.thread_comments (parent_id);

create table if not exists public.thread_reaction_marks (
    actor_id text not null,
    node text not null,
    entity_type text not null,
    entity_id text not null,
    target_kind text not null,
    comment_id text,
    reaction_id text not null,
    created_at timestamptz not null default now()
);

create unique index if not exists uq_thread_reaction_marks_root
    on public.thread_reaction_marks (actor_id, node, entity_type, entity_id, target_kind, reaction_id)
    where comment_id is null;

create unique index if not exists uq_thread_reaction_marks_comment
    on public.thread_reaction_marks (actor_id, node, entity_type, entity_id, target_kind, comment_id, reaction_id)
    where comment_id is not null;

create index if not exists idx_thread_reaction_marks_thread_key
    on public.thread_reaction_marks (node, entity_type, entity_id);

create table if not exists public.thread_attachment_refs (
    ref_id text primary key,
    comment_id text not null,
    media_type text not null,
    floor_class text not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_thread_attachment_refs_comment_id
    on public.thread_attachment_refs (comment_id);

alter table public.thread_threads enable row level security;
alter table public.thread_comments enable row level security;
alter table public.thread_reaction_marks enable row level security;
alter table public.thread_attachment_refs enable row level security;

drop policy if exists thread_threads_service_role_all on public.thread_threads;
create policy thread_threads_service_role_all
on public.thread_threads
for all
to service_role
using (true)
with check (true);

drop policy if exists thread_comments_service_role_all on public.thread_comments;
create policy thread_comments_service_role_all
on public.thread_comments
for all
to service_role
using (true)
with check (true);

drop policy if exists thread_reaction_marks_service_role_all on public.thread_reaction_marks;
create policy thread_reaction_marks_service_role_all
on public.thread_reaction_marks
for all
to service_role
using (true)
with check (true);

drop policy if exists thread_attachment_refs_service_role_all on public.thread_attachment_refs;
create policy thread_attachment_refs_service_role_all
on public.thread_attachment_refs
for all
to service_role
using (true)
with check (true);
