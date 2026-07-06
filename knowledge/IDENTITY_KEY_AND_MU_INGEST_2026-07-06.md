# Identity-key resolution (§15) + MU-sidecar ingest readiness — 2026-07-06

Handoff for the next Opus (cowork). All numbers queried live 2026-07-06 against
`slut_db/FRESH_2026/music_{v3,v4}.db` and the taghag Supabase (`rnscghanqopewyfxqjhp`).
Reproduce with the queries noted; don't inherit these on faith.

## 1. §15 identity key: `v3.content_sha256` vs `v4.file_hash_sha256` — THEY ARE NOT THE SAME VALUE

The crosswalk must NOT assume `v3.content_sha256 == v4.file_hash_sha256`. Evidence:

- **Value overlap:** only **2,810 / 30,472 (9.2%)** of v4 master hashes appear anywhere in
  `v3.asset_file.content_sha256`.
- **Same-file disagreement:** joining by basename, where the same file exists in both,
  **7,204 disagree vs 2,691 agree.** Different full-file SHA-256 for the same track.
- **Cause:** both are *full-file* SHA-256, computed at different times. MIK (and other tag
  writers) rewrote FLAC tags between the v3 and v4 hash computations, so the full-file hash
  diverged. The ~9% that still match are files not retagged in between. This is retagging,
  not corruption — but it means **`file_hash_sha256` is not a durable cross-time identity.**

### What each layer actually keys on (leave these alone)
- **The brain (Supabase) is internally consistent on `v4.file_hash_sha256`.** `audio_file`
  (31,383 rows, all with `checksum_sha256`; `file_key = "sha256:<hash>"`, `checksum_sha256 =
  "<hash>"`) was populated from v4 masters on this hash, and the MU sidecar filenames are this
  hash. The MU ingest join is clean (see §2). Do not re-key the brain to v3.
- **v4 has NO audio-only stable hash:** no `streaminfo_md5`; `acoustic_fingerprint` populated on
  only 643 / 30,507 (2%). The retag-invariant audio hash (`streaminfo_md5`) lives ONLY in v3.

### Recommended keys for the crosswalk rebuild
1. **Provider/release unification (the AA thread's actual job): key on `ISRC` + provider IDs**
   (`spotify_id`, `beatport_id` in v4 `track`/`track_identity`). ISRC covers **25,668 / 30,507
   (84%)** of v4 masters. This is the identity axis the crosswalk is about.
2. **Bridging brain(file) ↔ v3/providers: use the PATH bridge, not the SHA.** `v4.path`
   (relative) suffix-matches `v3.asset_file.path` (absolute) for **30,030 / 30,507 (98.4%)**.
   Via that bridge, `v3.streaminfo_md5` is reachable for 20,885 (68%) and `v3.content_sha256`
   for 9,888 (32%).
3. **If a durable per-file key is needed across time/layers**, adopt `streaminfo_md5`
   (retag-stable) — backfill it into the brain via the path bridge (68% available now; the
   remainder must be recomputed from the FLAC audio stream). Never the full-file SHA.

Operator stance (2026-07-06): *"i have no opinion when it comes to hashes"* — this is an
engineering call, governed by DECISIONS_LOCKED §15 (v4 load-bearing for the seam). §15 stands.

## 2. MU-sidecar ingest: READY, but NOT a "literal join"

`apple_track_analysis` currently holds ~42 rows; **~17,208 real sidecars sit ready** in
`hag/tools/apple_mu_analyses/<file_hash_sha256>.json` (skip-mocks are the tiny `{"skipped":true}`
files — exclude by size >300B or by parsing the flag).

- **Each sidecar is the raw ~5 MB Apple MusicUnderstanding blob** (`pace`, `loudness.{momentary,
  shortTerm,peak,integrated}`, `instrumentActivity`, `key`, `structurePredictions`, `rhythm`
  incl. `beatsPerMinute`, `structure`). It is NOT shaped like the target tables — there is a
  feature-engineering step (`taghag_import/apple_derived_features.py`, `apple_music_adapter.py`)
  that produced the existing rows.
- **Target = 3 tables, joined to `audio_file` via `source_artifact_sha256` = the sidecar's
  filename hash = `audio_file.checksum_sha256`** (join proven: 42/42 derived rows resolve):
  - `apple_analysis_runs` — provenance + `raw_result_json` (jsonb).
  - `apple_derived_features` — interpretable scalars (`apple_bpm`, `key_stable`,
    `pace_{mean,median,volatility,min,max}`, `*_intensity_mean`, `loudness_{integrated,peak,
    range_db,mean,std}`, `bpm_agreement_score`, counts) → the `apple_hybrid_v1` vector.
  - `apple_track_analysis` — mid-level curves (`global_bpm`, `key_mode/tonic`, `pace_curve`,
    `{drum,bass,vocal}_activity`, `loudness_{momentary,short_term}` jsonb).

### Blockers / decisions before batch-running
- **DO NOT store the raw 5 MB blob for all 17k.** `apple_analysis_runs.raw_result_json` × ~17k ×
  ~5 MB ≈ **~85 GB** — infeasible on the current tier. Decide: store derived + track_analysis
  only, keep the raw sidecars on disk as the archive, and either skip `raw_result_json` or store
  a compressed/trimmed subset. **This is the #1 thing to settle first.**
- **Don't run Gemini's `ingest_*.py` leftovers blind.** Use the `taghag_import.apple_*` path that
  produced the clean 42 rows; upsert idempotently on `source_artifact_sha256`; dry-run 10, verify,
  then batch.
- **`audio_file` has 31,383 rows vs 30,507 present masters (876 extra)** — dedupe/hygiene check
  before/after ingest.
