# Handover — taghag/tagslut — for the next Opus

**From:** a long session, 2026-07-05 ~03:30. **Operator:** Georges (sole dev).
**Read this, then boot properly (§0). Every load-bearing claim is tagged `[verified]` or `[assumed — check]`.**

---

## 0. Boot first
- Invoke the **`resolve-from-the-record`** skill. Read `~/Projects/tag/shared/STATE.md`, `shared/decisions/DECISIONS_LOCKED.md`, and the spine `shared/handoffs/handoff.jsonl`. Then read this file for the deltas.
- Real-machine work goes through **Desktop Commander** (the operator's py3.14 env, `/Volumes`, `~/.config`). The sandbox bash cannot see those.
- Repos: `~/Projects/tag/{hag,slut}`, DBs in `~/Projects/tag/slut_db/FRESH_2026/`. Never `?mode=ro` (APFS CANTOPEN). Never hand-edit the spine jsonl — use `shared/bin/handoff-append`.

---

## 1. THE DIRECTION — operator decision this session (RECORD IT; it is not yet on the ledger)
The operator is done treating v4 as the future. Decisive calls:
- **v4 is FROZEN.** Inert read-only catalog (DECISIONS_LOCKED §15). Not deleted (operator: "keep it if it won't become a burden"), **not fed, not invested in.** Do not grow it.
- **v3 stays the operational library.** Naming + metadata fixes happen on v3 / the files.
- **Supabase (taghag) IS the brain, and populating it is THE priority.**
- `[verified]` The brain joins to v3 on **`content_sha256`** (`audio_file.checksum_sha256`). **v4 is not in the path** — "nothing the operator touches depends on v4" held up under inspection.
- **Action:** record this direction in `DECISIONS_LOCKED` (supersede §15's v4-as-future assumption, cite this reasoning) + a spine note, so a future session doesn't drift back into feeding v4.

---

## 2. PRIORITY — populate the taghag Supabase brain
`[verified 2026-07-05]` Project **taghag** = `rnscghanqopewyfxqjhp` (ACTIVE, ap-southeast-2). The other (`taglsut` hqirw…) is the stale inactive dup — ignore.

**State: the brain is a complete schema with almost no data.** 19 tables, all **0 rows** except `track_embedding` = **744** — and those are orphaned because the `audio_file` seam is empty.

Seam = **`audio_file`** (`checksum_sha256`, `path`, `filename`, `identity_source`, `master_file_id`, size/duration/bitrate/sample_rate/codec). Everything hangs off `audio_file_id`.

Ingest plan (SHA-keyed throughout):
1. **Populate `audio_file`** from the ~30,507 present masters. Source: v4 `track_file` (path, `file_hash_sha256`, format, bitrate, sample_rate, duration_ms) or v3 `asset_file` (path, content_sha256, size). **Confirm which SHA matches the MU output filenames before loading.**
2. **`apple_track_analysis`** ← `hag/tools/apple_mu_analyses/<content_sha256>.json` — **already SHA-keyed, so ingest is a literal join, no matching.** (global_bpm, key, pace_curve, drum/bass/vocal_activity, loudness.)
3. **`dj_tag`** ← MIK energy (`~/Library/Application Support/Mixedinkey/Collection11.mikdb`, ~19k trajectory rows) + genre (from the trust ladder, §3) + bpm/key/isrc.
4. **`track_analysis`** ← Essentia moods (happy/aggressive/relaxed/party/danceability, genres_json) when that batch runs.
5. **Re-seat the 744 `track_embedding`** onto real `audio_file` rows.

**How:** check `hag/tools/` for existing Supabase ingest (`taghag_import analyze` already writes embeddings to Supabase) + service creds in `hag/.env`. **Bulk-load (psycopg2 / COPY / supabase-py), not row-by-row.** The Supabase MCP (`rnscghanqopewyfxqjhp`) is for verification queries, not 30k inserts. `[not started — teed up only]`

---

## 3. Other pending workstreams
- **#50 nature-gate ratification — NOT written down.** Operator ratified this session:
  1. **N-reject** as proposed — genre alone never excludes (only genre-excluded AND zero positive signals).
  2. **N4** — fires on Beatport **store BPM** (`ref_bp_track.bpm`), NOT measured BPM (double-tempo trap: RBX + MIK + Spotify all double). Red zone is the **140s**, and BPM is a *flag*, not the verdict — reject is decided by **genre + qualitative mood** (Essentia moods), **analysis-gated**.
  3. **Lexicon membership DROPPED** as a signal entirely (it's circular — it echoes the same tag garbage).
  4. **Beatport calibration test = yes** (not run).
  → Record in `DECISIONS_LOCKED`, close spine **#50** via `handoff-append`. Blocker #54 already cleared by #57 (ref_bp is slut's own ingest, migration 0019).
- **Genre / metadata clean.** `genre_trust.csv` (in `~/Projects/tag/`) tiers all 31,445 tracks: TRUSTED 8,879 / CORRECTABLE_bp 5,229 / UNVERIFIED 10,345 / MISSING 4,983 / SUSPECT_fallback 2,009. Correction ladder: **Beatport** `ref_bp_track` (authoritative, 14,108 on-Beatport) → **Spotify artist-genre** (mint a client-creds token from `SPOTIFY_CLIENT_ID/SECRET` in `.env` — no browser; proven: ANOHNI → `baroque pop`; ~11k are spotify_id-resolvable; some artists return `[]`) → **Essentia measured genre** (backstop for the empties). The blanket-"House" fallback is a *known* Apr-2026 bug (`slut/docs/archive/agent-session-outputs-2026-04-23/Audit Postman ↔ Tagger Scripts Connection.md` ~line 788) partially fixed on an old DB — never propagated to v4.
- **LISTENING_ARTISTS → `dj_admission='rejected'`.** Curated 248-artist list in `/Users/g/Reference/tagslut-readonly/legacy/handover/iceberg-prompts-2026-06-10/fable_iceberg_prompt.md` (the "iceberg" library-split plan — the ancestor of the nature gate; read it). Matches **3,925** v4 tracks. **MUST lose to Beatport/playlist presence** (~320 listening-artist tracks are Beatport-present = DJ-eligible). Wire after #50 is recorded.
- **Naming template fix — the operator's ORIGINAL ask, still undone.** Reposition the track number in the promote-time filename template so name-sort = track order. **Clarify the exact target format with the operator and preview before/after on ~10 files before touching anything.** File-layer change; needs no v4/Supabase.
- **Uncommitted code on `slut` branch `dev` (tested, commit them):**
  - `tagslut/cli/commands/intake.py` — redirect-gate fix: `_db_is_v3_intake_ready` now keys on the **`merged_into_id` column**, not row-presence (fixes a *self-poisoning* black-hole: leaked rows in v4 scaffolding used to flip the gate and route intake into v4 → crash).
  - `tests/cli/test_stage_v3_redirect.py` — rewritten + 2 incident-regression tests (7 pass).
  - `tools/ts-stage` — added `qobuz-dl|QobuzDownloads → qobuz` source mapping (operator switched to qobuz-dl Ultimate).
  - `tools/review/embed_cover_art.py` — art false-negative fix (embedded-art FLACs count as present, not "missing").
- **v4 hygiene (optional):** 65 harmless leaked scaffolding rows in `music_v4.db.asset_file` (killed-run residue; gate is schema-based now so inert). Purge if tidy-minded.

---

## 4. Background jobs (running at handoff — verify state)
- **MIK** energy pass — ~9.8k queue (dedup of a 30k import). Native output is the continuous energy *trajectory*, not a scalar.
- **Apple MU scan** — **DEAD** (last sidecar ~7h before this handover; it stalled early, coverage 2,621 of 30.5k (newest sidecar 03:20), NOT running). Restart `hag/tools/run_mu_scan.py` and let it finish; verify count with `ls hag/tools/apple_mu_analyses/*.json | wc -l`.
- **Spotify last-batch** — `spotify_ids_last_batch.txt` (2,488) via `fetch_automix_payloads.py`; **not currently running.** Payloads are intact in **both** `hag/automix_payloads/` (main store, ~27k files) and `hag/tools/automix_payloads/` (7,877) — ≈26,562 real analyses total, ≈ the whole fetchable universe. Count with `find <dir> -name '*.json' | wc -l` (NOT `ls *.json` — the big folder overflows the shell and falsely returns 0). Pass an absolute `--out` when fetching.
- **Rekordbox** — analyzing on **Normal** (high-precision off, per operator — it doesn't fix octave/double errors and RBX grid isn't the production grid). **Turn off RBX "write key to ID3"** to avoid clobbering MIK's Camelot.

---

## 5. Boundaries / discipline
- `resolve-from-the-record` before re-deciding anything; cite sources; escalate contradictions to the spine, don't silently pick.
- Never hand-append the spine (collision risk — see #52). Never write v4 at intake (redirect to `music_v3.db`). No `?mode=ro`.
- **Don't feed v4.** If you need the Beatport reference, it's `ref_bp_track` — read it, don't grow the v4 model.
- Verify inherited numbers before promoting them into a deliverable (this session, a "19,556 missing" scare was a two-folder artifact; the real remaining was ~2.5k).
- `content_sha256` is the universal seam (files ↔ v3 ↔ Supabase). Spotify payloads live in both `hag/automix_payloads/` (main store) and `hag/tools/automix_payloads/`; count with `find … -name '*.json' | wc -l`, not `ls *.json` (which overflows on the big folder).
- The operator wants two things: **a clean, correctly-named library** and **the mixing brain**. Stop adding architecture that serves neither.

**Key artifacts (all in `~/Projects/tag/`):** `genre_trust.csv`, `math.txt` (Spotify-fetch reconciliation), `needs_mik_rbx_analysis.m3u` (30,507 masters for MIK/RBX), `spotify_ids_last_batch.txt`.
