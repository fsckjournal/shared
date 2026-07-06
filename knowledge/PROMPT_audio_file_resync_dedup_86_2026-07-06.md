# PROMPT — `audio_file` re-sync + dedup to MASTER_LIBRARY (spine #86, the "paths thing")

Self-contained handoff. This **un-defers spine #86** (operator-deferred). Goal: make the brain's
`audio_file` table hold **exactly one master row per recording, matching the current
MASTER_LIBRARY**, sourced from slut/v4 (the identity system-of-record) — not blind brain writes.
Verify every number live; don't inherit on faith.

## The problem (verified, spine #86 / `SUPABASE_RESUME_2026-07-07.md`)
`audio_file` is **not synced to MASTER_LIBRARY**. It carries:
- **pre-promotion STAGING paths** (analysis-time paths under staging / lossy / PLAYGROUND), and
- **duplicate lossy rows per recording** (not one master row per track),
and it **trails on-disk MASTER_LIBRARY (~32,833 files) by ~1,450**. Row count **31,383** vs ~30,507
present v4 masters (≈876 stale non-master rows on top of the dup problem).

This single drift is the **root cause** of: every path-based undercount, the **3,691 unplaced
`key_camelot`** (#85), and the streaminfo/hygiene mismatches.

## Why it's gated / whose lane
- It is a **write to `audio_file`** — that's the part the operator deferred. This prompt = green light.
- **Identity/path is slut's system-of-record (§7).** The re-sync source of truth is **slut/v4**
  (`track_file` `present=1` + `content_sha256`) via the identity-seam export
  (`slut:tools/v4/export_identity_seam.py`), **not** stale rekordbox/MIK paths and not blind brain edits.
- **F-022 is open and related:** MASTER_LIBRARY drift (300 hash mismatches, 938 missing files, spine
  #67/#20). Reconcile the library-drift question before writing rows that assume files exist.

## Artifacts already prepared
- `shared/knowledge/plus_missing_not_in_brain_2026-07-06.csv` — the 1,213 "not in brain" rows (mostly
  feat./punctuation **false**-missing + genuinely-new; only ~120 truly gone).
- `~/Documents/plus-missing.xml` — fresh rekordbox export, 26,044 MASTER_LIBRARY tracks.
- `crosswalk_v3v4_identity` (Supabase table, 30,507 rows) — `v4_file_hash_sha256 =
  audio_file.checksum_sha256`, carries `isrc`, `track_id`, `v3_streaminfo_md5`.

## Approach
1. **Ground truth** = the current MASTER_LIBRARY masters, **one FLAC per recording**, from slut/v4
   `track_file present=1` (+ `content_sha256`/`file_hash_sha256`). Never derive the master set from a
   stale MIK/rekordbox bookmark path.
2. **Classify** every `audio_file` row: (a) staging/lossy path, (b) duplicate-lossy per recording,
   (c) ~876 stale non-master, (d) genuinely-missing master not yet in brain.
3. **Re-sync** by regenerating the identity seam from slut/v4 and upserting `audio_file` to **one
   master row per recording** (keyed on `file_hash_sha256`/`checksum_sha256`); merge/drop dups, add the
   genuinely-new, retire the stale. **Preserve the `streaminfo_md5` backfill (#89)** — re-map it onto
   the reconciled rows via `crosswalk_v3v4_identity`, don't lose it.
4. **Re-run dependents** after re-sync: place the 3,691 unplaced `key_camelot` (#85), re-check
   `bpm_agreement_score`, streaminfo coverage — counts should now reconcile against MASTER_LIBRARY.
5. **Verify:** `count(audio_file) == distinct masters`; 0 staging paths; 0 duplicate recordings;
   3,691 unplaced keys resolved; streaminfo preserved; DB size within the 166 MB free-tier headroom.

## Gotchas (hard-won — `SUPABASE_RESUME_2026-07-07.md`)
- **Feat./punctuation false-missing:** an en-dash `–`, a `feat.`, or a punctuation variant reads as
  "missing" on a naïve path match. This is what flipped a "1,213 missing" scare to ~120 truly gone —
  re-resolve by identity (artist+title / content hash), never by raw path equality.
- **Stale analysis-time paths:** MIK/rekordbox bookmark paths are the *analysis-time* location
  (staging/lossy/PLAYGROUND) and go stale after promote — a stale path is NOT proof of "missing."
- **F-022 first:** 938 files are genuinely missing on disk; reconcile the drift before writing rows.
- **MCP flaky** → REST/service key or Supabase CLI. Sandbox has a 45 s bash cap + no background jobs;
  run bulk work on the Mac via local shell.
- **Not this lane:** pool *membership* is Essentia mood + `sonic7_v1` embeddings — this re-sync fixes
  identity/coverage, not membership.

Spine arc to cite: #86 (this item, deferred), #85 (unplaced keys it unblocks), #89 (streaminfo to
preserve), #67/#20 (F-022 drift), §7 (identity = slut's system of record).
