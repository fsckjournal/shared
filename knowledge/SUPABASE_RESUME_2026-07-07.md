# Supabase (taghag brain) — resume handoff, 2026-07-07

Boot doc for the next session. **Supersedes `SUPABASE_RESUME_2026-07-06.md`** (that doc's OPEN
items #1/#2/#5 are now DONE; read this one first). Everything below was queried/applied live
2026-07-06 (PM) against project `rnscghanqopewyfxqjhp`. **Reproduce; do not inherit on faith.**
Spine events for this arc: **#83–#87** (`tag/shared/handoffs/handoff.jsonl`).

## Connection facts (verified)
- **Project:** `rnscghanqopewyfxqjhp` (org `fsckjournal` / `aemxhwxiqmvowxdhywhs`). Postgres 17.6.
- **Plan: FREE — hard 500 MB DB limit.** Live size **334 MB** (`pg_database_size`, 350,243,987 bytes,
  incl. auth/storage/system) → **166 MB free (~33%)**. This arc's additions (`key_camelot` + 30,507-row
  crosswalk) cost ~24 MB. Biggest tables: `apple_analysis_runs` 108 MB + `track_cue` 77 MB = 55% of the DB
  (verify: `supabase inspect db table-stats --linked`). **`streaminfo_md5` backfill (#2) adds only a few
  MB → storage is NOT a blocker; only the operator deferral is.** (spine #88)
- **Owner user id:** `d4c61173-8432-432f-b238-9bd72c7285e3` (single owner; all rows).
- Creds for a *local* run in `hag/.env`: `TAGHAG_SUPABASE_URL`, `TAGHAG_SUPABASE_SECRET_KEY`
  (service role), `TAGHAG_OWNER_USER_ID`. REST bulk load uses the secret key (works when MCP is down).
- ⚠️ **The Supabase MCP was intermittently down / disconnected this session.** Fallbacks that work:
  (a) REST/PostgREST with the service key for reads + bulk writes; (b) the **Supabase CLI** (linked in
  `hag/supabase`) for DDL/migrations. See "CLI reconcile procedure" below — it is NOT trivial.

## What is DONE this session (verify — do not trust)
```sql
select
 (select count(*) from apple_derived_features where bpm_agreement_score is not null) bpm_agree,   -- 16826
 (select count(*) from apple_derived_features where bpm_agreement_score is null)      bpm_null,    -- 2993
 (select count(*) from dj_tag where tag_source='rekordbox_xml' and key_camelot is not null) key_cam, -- 24571
 (select count(*) from dj_tag where tag_source='rekordbox_xml'
    and key_camelot is not null and key_camelot !~ '^(1[0-2]|[1-9])[AB]$')             key_bad,     -- 0
 (select count(*) from crosswalk_v3v4_identity)                                        xwalk,       -- 30507
 (select count(*) from audio_file)                                                     af;          -- 31383
```
1. **`bpm_agreement_score` backfilled** (spine #83) — 16,826 filled / 2,993 NULL, avg 0.840, all in [0,1].
   Reference = **Rekordbox** measured BPM (`dj_tag` `tag_source='rekordbox_xml'.bpm`), validated 99.9%
   against the live rekordbox `master.db`. 2,993 NULL = genuinely absent from Rekordbox (correct).
   827 of the 2,015 zeros are double/half-time (no octave folding — matches the code path).
2. **`dj_tag.key_camelot` backfilled** (spine #85) — 24,571 rows, 100% valid Camelot, covering 16,371 MU
   tracks. Source = **MIK DB** `Collection11.mikdb` `ZSONG.ZKEY` (clean Camelot A/B), path-joined to
   `audio_file`. The rekordbox XML/DB key field is CONTAMINATED (~40% reloaded pre-MIK tags) — do NOT use
   it. `apple_key` is a corroborator (~78% agree), NOT the key authority.
3. **`crosswalk_v3v4_identity` created + loaded** (spine #87) — all 30,507 rows. 29,519 join to
   `audio_file.checksum_sha256` via `v4_file_hash_sha256`; 20,556 carry `v3_streaminfo_md5`. Indexes on
   `v4_file_hash_sha256`, `isrc`, `track_id`.

## Decisions locked this arc (do NOT re-litigate — cite the record)
1. **`DECISIONS_LOCKED §12` — analysis authority by PROVENANCE (measured vs provider), not tool.**
   Trusted **measured** map (all hag-lane): **KEY = MIK** (stored **Camelot** — MIK-proprietary, self-
   identifying + convertible), **BPM = Rekordbox** (MIK writes no tempo), **ENERGY = MIK** (per-cue
   trajectory). Provider key/BPM (`canonical_key`/`canonical_bpm`, Beatport/Lexicon) stay **slut's** and
   are never overwritten. A measured-vs-provider agreement score must use a **measured** reference —
   never a provider BPM. (§12 sub-bullet added operator-directed 2026-07-06, pending 3-way ack.)
2. **Source of truth = the DBs, not the XML exports.** rekordbox XML `Tonality` / master.db `ScaleName`
   are contaminated with reloaded pre-MIK tags. MIK `ZSONG.ZKEY` (Camelot A/B) is the clean key;
   rekordbox `djmdContent.BPM` (×100) is the clean BPM.
3. **Crosswalk join keys:** `crosswalk.v4_file_hash_sha256 = audio_file.checksum_sha256`;
   `v3_streaminfo_md5` = retag-stable audio hash (the durable per-file key for #3).

## Hard-won operational lessons (save yourself the pain)
- **MIK bookmark paths are UTF-8.** `ZBOOKMARKDATA` blobs embed the POSIX path; decode the path bytes as
  **UTF-8** (`bytes.decode('latin-1')` to scan, then `.encode('latin-1').decode('utf-8')`). A latin-1
  decode mojibakes the en-dash `–` and collapses the `audio_file` path-join from ~28k to 53.
- **MIK bookmark path is the *analysis-time* path (staging/lossy/PLAYGROUND), goes STALE after promote.**
  Do not treat a stale MIK/rekordbox path as "missing." Re-resolve by identity (artist+title / filename)
  or by content hash. This flipped a "1,213 missing" scare down to ~120 genuinely-gone.
- **`GREATEST(0.0, NULL)` returns `0.0`, not NULL** (Postgres GREATEST/LEAST ignore NULLs). A naïve
  `greatest(0, 1-(…NULL…))` scores *unmatched* rows 0.0. INNER-join the ref so unmatched stay NULL.
- **Supabase CLI can't hand `psql` a password** — it mints an *ephemeral login role* via the mgmt API
  (access token in keychain, service "Supabase CLI"). `db push` is blocked if remote migration history
  has records with no local files (earlier MCP/dashboard applies cause this). **Reconcile procedure that
  worked:** create matching local migration files for the orphaned remote versions (idempotent, e.g.
  `add column if not exists`), `supabase migration repair --status reverted <remote-only ids>` +
  `--status applied <local ids>` to align, then `supabase db push` applies only the truly-new migration.
  Do NOT follow the CLI's positional repair suggestion blindly — it can mispair an unrelated new
  migration as "applied" and skip creating your table. Data load: REST service key (no password needed).
- **Sandbox** has a 45 s/bash cap + no background jobs; run bulk work on the Mac via the local shell.

## OPEN work — priority order (all remaining items are `audio_file` writes; operator DEFERRED the re-sync)
1. **[#86, DEFERRED by operator] `audio_file` re-sync + dedup to MASTER_LIBRARY.** `audio_file` carries
   pre-promotion **staging** paths + **duplicate lossy** rows per recording, and trails the on-disk
   MASTER_LIBRARY (~32,833 files) by ~1,450. Root cause of every path-based undercount + the 3,691
   unplaced keys. Identity/path is **slut's system of record (§7)** → re-sync should come from slut/v4,
   not blind brain writes. Full "not in brain" list: `knowledge/plus_missing_not_in_brain_2026-07-06.csv`
   (1,213 rows = feat./punctuation false-missing + genuinely-new). Fresh rekordbox export with the
   promoted tracks: `~/Documents/plus-missing.xml` (26,044 MASTER_LIBRARY tracks).
2. **`streaminfo_md5` backfill into `audio_file` (was #3).** NOW UNBLOCKED as an in-SQL join (crosswalk is
   loaded): add nullable `streaminfo_md5` column, `UPDATE audio_file a SET streaminfo_md5 = x.v3_streaminfo_md5
   FROM crosswalk_v3v4_identity x WHERE x.v4_file_hash_sha256 = a.checksum_sha256` (~20,150 fillable).
   Hash join → **independent of the #86 path drift**. Still a *write* to `audio_file` → gated by the deferral.
3. **`audio_file` hygiene (was #4).** ~876 stale non-master rows + the staging/lossy dup rows (see #1).
   Clean up before/with the streaminfo backfill so counts reconcile.
4. **[#85] 3,691 unplaced `key_camelot`** — MIK-keyed `audio_file`s with no `rekordbox_xml` row (per the
   chosen storage). Place via a `mik`-source row or a 1:1 table for full coverage. Gated by #1.
5. **[library, not brain] Acquisition / reanalysis** — `missing_reanalyze.m3u8` (1,107 located, mostly
   already in MASTER_LIBRARY — reanalyze in MIK to refresh stale bookmarks), `needs_analysis_delta.m3u`
   (76 present-but-unqueued), `reacquire.csv` (~103 truly gone). Out of the brain's lane.

## Git / repo state
- **2 new migration files need committing** (`hag/supabase/migrations/`):
  `20260706113545_add_dj_tag_key_camelot.sql`, `20260706180000_create_crosswalk_v3v4_identity.sql`.
- Migration history was `migration repair`'d this session to align local↔remote (drift from earlier
  MCP applies). `supabase migration list --linked` should now show all-aligned except any new pending.

## NOT this lane (bigger picture)
Pool *membership* is gated by **Essentia mood/danceability + `sonic7_v1` embeddings**, not Apple MU / MIK /
Rekordbox (those are enrichers). MU/key/BPM ingest improves *mix quality*, not membership.
See `hag/docs/automix/POOL_DEFINITION.md`.

## Key files & artifacts
- `hag/tools/taghag_import/apple_derived_features.py` — `_bpm_agreement_score` (formula reproduced for #83).
- MIK DB: `~/Library/Application Support/Mixedinkey/Collection11.mikdb` (`ZSONG.ZKEY` = trusted key).
- Rekordbox DB: `~/Library/Pioneer/rekordbox/master.db` (SQLCipher; key
  `402fd482c38817c35ffa8ffb8c7d93143b749e7d315df7a81732a1ff43608497`, `cipher_compatibility=4`; BPM ×100).
- `Projects/crosswalk_v3v4_identity_2026-07-06.csv` (30,507; now also the `crosswalk_v3v4_identity` table).
- `knowledge/plus_missing_not_in_brain_2026-07-06.csv` (the #86 1,213 list).
- Spine: `tag/shared/handoffs/handoff.jsonl` — #83 (bpm_agreement), #84 (bpm provenance/§12 check),
  #85 (key_camelot + §12 key sub-bullet), #86 (audio_file drift, DEFERRED), #87 (crosswalk load).
