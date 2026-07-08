# Prompt — `streaminfo_md5` backfill (for Opus, new session)

**Task:** Backfill `audio_file.streaminfo_md5` in the taghag Supabase brain (project
`rnscghanqopewyfxqjhp`) from the `crosswalk_v3v4_identity` table. This is the one open write left from
resume item #3. **First read `tag/shared/knowledge/SUPABASE_RESUME_2026-07-07.md`** for full context and
the tooling caveats — reproduce its numbers live, don't inherit on faith — then do this single backfill.

**Why:** `streaminfo_md5` is the retag-stable, audio-only per-file hash (v3-only). It's the durable
identity key that survives MIK/Rekordbox retagging, whereas v4's `file_hash_sha256` changes on every
retag. The crosswalk carries it; `audio_file` doesn't yet.

## Steps
1. **Verify first (don't trust):** `crosswalk_v3v4_identity` ≈ 30,507 rows, ~20,556 with
   `v3_streaminfo_md5`; `audio_file` ≈ 31,383 rows, no `streaminfo_md5` column yet. Join key
   `crosswalk.v4_file_hash_sha256 = audio_file.checksum_sha256` (~29,519 joinable). This is a **hash
   join — independent of the #86 `audio_file` path drift.**
2. **Add the column** via a numbered migration:
   ```sql
   alter table public.audio_file add column if not exists streaminfo_md5 text;
   ```
3. **Backfill:**
   ```sql
   update audio_file a
   set streaminfo_md5 = x.v3_streaminfo_md5
   from crosswalk_v3v4_identity x
   where x.v4_file_hash_sha256 = a.checksum_sha256
     and x.v3_streaminfo_md5 is not null;
   ```
   (~20,150 rows expected.)
4. **Verify:** filled count, all values 32-hex (`streaminfo_md5 ~ '^[0-9a-f]{32}$'`), spot-check a
   couple against the crosswalk CSV.
5. **Commit** the migration file with
   `~/Projects/tag/shared/bin/git-safe commit -m "…" <path>` (raw `git commit` is blocked in the shared
   tag repos; `git-safe` is a script, not on PATH). Append a spine note to
   `tag/shared/handoffs/handoff.jsonl` (next id after #88).

## Tooling
- **MCP up:** use `apply_migration` + `execute_sql` (simplest).
- **MCP down:** use the linked Supabase CLI in `hag/supabase`. It mints an ephemeral login role (so
  `psql` can't get a password), and `db push` may be blocked by migration-history drift — reconcile
  with matching local migration files + `supabase migration repair` **before** pushing (full procedure
  in the boot doc's "Hard-won lessons"). Data-only writes can also go via PostgREST with the service key
  in `hag/.env`.

## Do NOT
- Touch the `audio_file` re-sync/dedup (#86) — operator-deferred, and this backfill doesn't need it.
- Worry about storage — 166 MB free; this adds a few MB (spine #88).
