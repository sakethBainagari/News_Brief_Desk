-- PostgreSQL / Supabase compatible database schema.

create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

create table if not exists users (
  id uuid primary key default coalesce(uuid_generate_v4(), gen_random_uuid()),
  name text not null,
  email text unique not null,
  role text not null check (role in ('REPORTER', 'EDITOR', 'DESK_HEAD')),
  password_hash text,
  created_at timestamptz not null default now()
);

create table if not exists raw_items (
  id uuid primary key default coalesce(uuid_generate_v4(), gen_random_uuid()),
  source_name text not null,
  headline text not null,
  body text not null,
  category text,
  source_published_at timestamptz,
  ingested_at timestamptz not null default now(),
  embedding_status text not null default 'PENDING'
);

create table if not exists story_clusters (
  id uuid primary key default coalesce(uuid_generate_v4(), gen_random_uuid()),
  canonical_headline text,
  category text,
  status text not null default 'CLUSTERED'
    check (status in ('CLUSTERED', 'DRAFT', 'EDITOR_REVIEW', 'PUBLISHED', 'MERGED')),
  confidence numeric(5,4),
  confidence_reason text,
  first_incoming_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists story_sources (
  story_id uuid not null references story_clusters(id) on delete cascade,
  raw_item_id uuid not null references raw_items(id) on delete cascade,
  match_label text check (match_label in ('SAME_EVENT', 'DIFFERENT_EVENT', 'UNCERTAIN')),
  match_confidence numeric(5,4),
  match_reason text,
  primary key (story_id, raw_item_id)
);

create table if not exists briefs (
  id uuid primary key default coalesce(uuid_generate_v4(), gen_random_uuid()),
  story_id uuid not null references story_clusters(id) on delete cascade,
  reporter_id uuid references users(id),
  editor_id uuid references users(id),
  headline text not null,
  summary text not null,
  status text not null default 'DRAFT'
    check (status in ('DRAFT', 'EDITOR_REVIEW', 'PUBLISHED', 'CHANGES_REQUESTED')),
  created_at timestamptz not null default now(),
  submitted_at timestamptz,
  published_at timestamptz
);

create table if not exists story_merges (
  id uuid primary key default coalesce(uuid_generate_v4(), gen_random_uuid()),
  source_story_id uuid not null references story_clusters(id),
  target_story_id uuid not null references story_clusters(id),
  merged_by uuid references users(id),
  reason text,
  merged_at timestamptz not null default now()
);

create table if not exists audit_logs (
  id uuid primary key default coalesce(uuid_generate_v4(), gen_random_uuid()),
  actor_id uuid references users(id),
  action text not null,
  entity_type text not null,
  entity_id uuid,
  metadata jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_raw_items_ingested_at on raw_items(ingested_at);
create index if not exists idx_raw_items_category on raw_items(category);
create index if not exists idx_story_clusters_status on story_clusters(status);
create index if not exists idx_briefs_status on briefs(status);
create index if not exists idx_briefs_published_at on briefs(published_at);
