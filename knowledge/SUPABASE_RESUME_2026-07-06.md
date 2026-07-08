# Supabase (taghag brain) — resume handoff, 2026-07-06

Boot doc for the next session picking up the taghag Supabase work. Everything below
was queried live 2026-07-06 against project `rnscghanqopewyfxqjhp`. **Reproduce; do not
inherit on faith.** Spine events for this arc: #75, #76, #80, #81 (`tag/shared/handoffs/handoff.jsonl`).

## Connection facts (verified)
- **Project:** `rnscghanqopewyfxqjhp` (org `fsckjournal` / `aemxhwxiqmvowxdhywhs`).
- **Plan: FREE — hard 500 MB DB limit.** This governs every storage decision below. Current size **310 MB** (~190 MB headroom).
- **Owner user id:** `d4c61173-8432-432f-b238-9bd72c7285e3` (single owner; all rows).
- Creds for a *local* run live in `hag/.env`: `TAGHAG_SUPABASE_URL`, `TAGHAG_SUPABASE_SECRET_KEY` (service role), `TAGHAG_OWNER_USER_ID`. The `VITE_*` vars are frontend-only.

## What is DONE (Apple MU sidecar ingest)
The MU brain is fully populated, **scalars-only**, and clean. Verify:
```sql
select
 (select count(*) from apple_derived_features) adf,              -- 19819
 (select count(distinct audio_file_id) from apple_derived_features) adf_files, -- 19819 (1 row/file)
 (select count(*) from apple_track_analysis) ata,                -- 19819
 (select count(*) from apple_analysis_runs) runs,               -- 19857 (+38 legacy POC)
 (select count(*) from apple_derived_features d
    where not exists (select 1 from audio_file a where a.id=d.audio_file_id)) orphan_fk, -- 0
 (select count(*) from apple_track_analysis
    where drum_activity is not null or loudness_momentary is not null) curves_remaining, -- 0
 (select count(*) from apple_derived_features where apple_key is not null) key_filled,   -- 19755
 (select count(*) from apple_derived_features where apple_bpm is null) bpm_null;         -- 0
```
- One row per `audio_file_id` in each table, **0 orphaned FKs**, **0 duplicate files**.
- `apple_track_analysis` is uniformly **scalars-only** (`global_bpm`, `key_tonic`, `key_mode`,
  `loudness_integrated`, `loudness_peak`); all curve columns NULL on all 19,819 rows.
- `apple_derived_features` = the 27 scalars feeding `apple_hybrid_v1`; `apple_key` now 19,755 filled / 64 keyless-NULL.
- `apple_analysis_runs.raw_result_json` holds a **~KB trimmed provenance stub**, NOT the ~5 MB blob.

## Decisions locked this arc (do NOT re-litigate — see spine)
1. **Ingest is sidecar-driven, keyed `filename == audio_file.checksum_sha256 → audio_file_id` (FK).**
   `source_artifact_sha256` is the canonical-JSON hash of the sidecar — an idempotency/provenance
   key, **NOT** a join key. The "42/42 join" is via the `audio_file_id` FK.
2. **Do NOT use `taghag_import.apple_music_adapter.run_apple_music_ingestion` for sidecars** — it
   re-runs the Swift analyzer on FLACs and stores the 5 MB blob. Wrong tool. The correct, tested
   path is **`hag/tools/ingest_mu_sidecars_scalars.py`** (idempotent, resumable, scalars-only).
3. **Scalars-only, forced by the 500 MB free tier.** Full activity/loudness curves ≈ 260 KB/row ×
   18k ≈ **4.4 GB** — infeasible. `raw_result_json` NOT NULL → trimmed stub (not blob).
4. **Curves are NOT stored in Postgres and nothing reads them there.** `apple_hybrid_v1` uses
   derived *scalars*; `mixslice/render_transition.py` reads curves **from the on-disk sidecars**,
   not the DB. The raw sidecars are the archive of record.

## Hard-won operational lessons (save yourself the pain)
- **The cowork sandbox has a 45 s-per-bash-call cap and cannot run background jobs** (`nohup`/`setsid`
  are killed at the call boundary). Every timeout leaves an **orphan python that steals all 4 cores
  and Supabase rate-limit budget**, cascading more timeouts. Reading/parsing 128 GB / 19k sidecars
  in-session is NOT viable.
- **For any bulk sidecar work, run the local script on the Mac** (native FS, no cap): it did 17,960
  rows in ~30 min. In-session, prefer the Supabase MCP `execute_sql` for SQL, and reserve sandbox
  `requests`/python for small compute.
- Trimmed/deleted rows don't reclaim disk until autovacuum (free tier: no `VACUUM FULL` in a txn).

## DONE 2026-07-06 (PM session — spine #83)
1. **[disk] Sidecars moved to ATTIC — DONE.** `hag/tools/apple_mu_analyses` is now a symlink →
   `/Volumes/ATTIC/taghag_mu_sidecars` (144 GB, 22,146 sidecar JSONs), `_apple_mu_old` removed,
   ATTIC 49% used / 959 GB free. (Note: 22,146 sidecars vs 19,819 ingested rows = ~2,327 gap,
   likely legacy/POC or unjoinable — not yet reconciled.)
2. **`bpm_agreement_score` backfilled — DONE. Reference = Rekordbox (per Georges), not MIK.**
   - Source: `dj_tag` where `tag_source='rekordbox_xml'` (`bpm` column), joined to
     `apple_derived_features` via `audio_file_id`.
   - **Provenance (why Rekordbox is correct, not just operator-chosen):** `DECISIONS_LOCKED §12`
     assigns feature authority by **provenance (measured vs provider), not tool**. `bpm_agreement_score`
     scores Apple MU's *measured* BPM against a reference, so the reference MUST also be **measured**
     (hag's lane); Rekordbox BPM is a measured value (§12 lists it among measurers). ⚠️ The earlier
     framing "backfill from **MIK/provider** BPM" (spine #82) is §12-loose: a *provider* BPM
     (`ref_bp_track.bpm`, v4 `canonical_bpm` — Beatport/Lexicon, slut's lane) as the reference would
     **violate §12** (measured-vs-provider). Do NOT swap the reference to a provider BPM. Corroborated
     by the record: a prior session logged feeding `master.xml` into slut's v4 `track.bpm` as
     "corrupting the provider-sourced column" — same boundary, opposite direction.
   - **Validated against LIVE Rekordbox `master.db`** (SQLCipher; key
     `402fd482c38817c35ffa8ffb8c7d93143b749e7d315df7a81732a1ff43608497`, `cipher_compatibility=4`;
     BPM stored ×100 in `djmdContent`; join `audio_file.path == djmdContent.FolderPath`). Snapshot
     vs live: **99.9% identical BPM** (24,460/24,489; 29 differ, 13 by >5). `live-only=0` → the
     `rekordbox_xml` snapshot is the better key (covers 514 more MU tracks than a live path-join).
   - Result: **16,826 filled / 2,993 NULL** (NULL = genuinely absent from Rekordbox — correct per
     `_bpm_agreement_score` returning None on missing ref). avg **0.840**, exact(1.0)=8,877,
     zeros(0.0)=2,015, near[0.9,1)=4,263, range [0,1].
   - Formula reproduced verbatim from `apple_derived_features.py`:
     `round(max(0, 1 - (|apple-ref|/max(apple,ref))/0.10), 3)`. **No octave folding** — so **827 of
     the 2,015 zeros are double/half-time** (Apple detected 2×/0.5× the Rekordbox tempo). Left as-is
     to stay consistent with the ingest code path; candidate future improvement (octave-fold variant).
   - ⚠️ **GREATEST(0.0, NULL) trap:** Postgres `GREATEST`/`LEAST` ignore NULLs, so a naïve
     `greatest(0.0, 1 - (…NULL…))` scores *unmatched* rows **0.0 instead of NULL** (this inflated an
     early count to 5,008 = 2,015 real + 2,993 phantom). The applied UPDATE guards this by INNER-joining
     the ref CTE (only matched rows written), leaving unmatched NULL.

## DONE 2026-07-06 (trusted KEY backfill — spine #85, ledger §12)
- **Trusted measured-source map (all §12 hag-lane): KEY=MIK, BPM=Rekordbox, ENERGY=MIK.** Locked as a
  `DECISIONS_LOCKED §12` sub-bullet (operator-directed, pending 3-way ack). Measured key = MIK, stored
  **Camelot** (MIK-proprietary → self-identifying + convertible). Provider key (`canonical_key`) stays
  slut's, never overwritten.
- **Source of truth = the DBs, not the XML.** The rekordbox XML/DB `Tonality`/`ScaleName` key is
  **contaminated**: ~40% are reloaded pre-MIK tags (Camelot-class agrees w/ Apple 76%; Open-Key/musical
  only ~55%; per-track vs MIK ZKEY only 71%). Clean truth = **MIK DB** `Collection11.mikdb` `ZSONG.ZKEY`
  (pure Camelot A/B). MIK analyzed the master FLACs directly → 31,502/33,615 ZKEY rows carry
  `/Volumes/MUSIC/MASTER_LIBRARY/*.flac` bookmark paths → **path-joins to `audio_file`** (same join as BPM).
  ⚠️ MIK bookmark blobs are UTF-8; decode the path bytes as UTF-8 (a latin-1 decode mojibakes the en-dash
  and drops the join from 28k to 53).
- **Applied:** new column `dj_tag.key_camelot`; wrote path-joined MIK ZKEY onto `rekordbox_xml` rows =
  **24,571 filled** (100% valid Camelot; dist matches MIK ZKEY 8A/5A/7A/6A/9A), covering **16,371 / 19,819
  MU tracks**. Validation: MIK ZKEY vs Apple `apple_key` **78.0%** (= clean-class baseline; gap = normal
  cross-detector variance, not error). `apple_key` is **demoted to corroborator**, not the key authority.
- **OPEN:** 3,691 MIK keys unplaced — those `audio_file`s have no `rekordbox_xml` row (per the chosen
  storage: key on the rekordbox_xml row). To reach full coverage, place them via a `mik`-source row or a
  1:1 table. Converter (Open-Key `M`/`D` = `((n+6)%12)+1`, `D`→B/`M`→A; musical→Camelot) validated aggregate
  Pearson **0.995** vs MIK ZKEY. Repro: `~/Library/Application Support/Mixedinkey/Collection11.mikdb`.

## OPEN work — priority order
3. **`streaminfo_md5` backfill into `audio_file` (deferred from the crosswalk / Session 2).** v4 has no
   retag-invariant audio hash; `streaminfo_md5` (v3-only, retag-stable) is the durable per-file key.
   Plan: add a nullable `streaminfo_md5` column via a numbered migration, then UPDATE keyed on
   `checksum_sha256 = v4.file_hash_sha256` using `Projects/crosswalk_v3v4_identity_2026-07-06.csv`
   (~20,150 realistically joinable; the crosswalk's upper bound was 20,883 but `audio_file` is ~96.5%
   synced to current masters — re-sync first). This is a *write* to `audio_file`; it was deferred to
   avoid colliding with the ingest session.
4. **`audio_file` hygiene:** 31,383 rows vs 30,507 present masters = **876 stale non-master rows**
   (all `checksum_sha256` distinct, 0 dup keys — harmless to the MU join, but clean up before the
   streaminfo backfill so counts reconcile).
5. **Load the crosswalk into the DB — DONE (spine #87).** Table `public.crosswalk_v3v4_identity`
   created + loaded with all **30,507 rows** (14 cols; year int, flags bool). Verified: 30,472 distinct
   `v4_file_hash_sha256`, **29,519 joinable** to `audio_file.checksum_sha256`, 20,556 rows carry
   `v3_streaminfo_md5`. Indexes on `v4_file_hash_sha256`, `isrc`, `track_id`.
   - **Method (MCP was down → used the Supabase CLI, per operator):** the CLI can't hand `psql` a
     password (it mints an ephemeral login role), and `db push` was blocked by pre-existing
     migration-history drift (remote had 4 records with no local files, from earlier MCP applies). Fixed
     it: added local files `20260706113545_add_dj_tag_key_camelot.sql` (idempotent, documents the already-
     applied key column) + `20260706180000_create_crosswalk_v3v4_identity.sql`, `migration repair`'d the
     idempotent trio (reverted the 3 remote-only IDs, applied the 3 local IDs), then `db push` applied
     only the crosswalk. Data loaded via REST (service key). **⚠️ Two new migration files in
     `hag/supabase/migrations/` need committing.**
   - **This unblocks #3:** the `streaminfo_md5` backfill is now a clean in-SQL join
     `crosswalk.v4_file_hash_sha256 = audio_file.checksum_sha256` → set `streaminfo_md5 = v3_streaminfo_md5`
     — **independent of the #86 path drift** (hash join, not path). Still a *write* to `audio_file`, so
     gated by the same deferral.

## NOT this lane (bigger picture, don't confuse with MU work)
Pool *membership* is gated by **Essentia mood/danceability + `sonic7_v1` embeddings**, not Apple MU
(MU is an enricher). Only ~236 tracks are "eligible now"; ~30k need an Essentia pass + embedding
recompute. See `hag/docs/automix/POOL_DEFINITION.md`. MU ingest (done) improves *mix quality*, not
membership.

## Key files
- `hag/tools/ingest_mu_sidecars_scalars.py` — the tested ingest (resumable, idempotent).
- `hag/tools/taghag_import/apple_derived_features.py` — `compute_derived_features` (now handles
  string tonic/mode; `apple_key` fix landed this session).
- `Projects/crosswalk_v3v4_identity_2026-07-06.csv`, `Projects/crosswalk_report_2026-07-06.md`.
- `tag/shared/knowledge/IDENTITY_KEY_AND_MU_INGEST_2026-07-06.md` — the prior §15/ingest handoff.
- Spine: `tag/shared/handoffs/handoff.jsonl` events #74 (crosswalk), #75/#76/#80/#81 (this arc).
