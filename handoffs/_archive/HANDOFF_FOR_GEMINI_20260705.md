# Handover for Gemini — taghag/tagslut project — 2026-07-05

You are picking up a music-library project from a long Claude session. You do **not** share
Claude's context, so this file spells out every path and term. Read §A (glossary) and §B
(file map) first — everything after refers back to them.

---

## A. Glossary — what the words mean

- **v3** = `music_v3.db`, a SQLite database. This is the **operational** library — the intake
  pipeline writes here. It's the live system of record. **Keep using it.**
- **v4** = `music_v4.db`, a second SQLite database — a normalized rebuild of v3.
  **Status: read-only but LOAD-BEARING — not dispensable.** Never *write* to it. But the brain
  population *reads* it, because it holds the complete file hashes (`track_file.file_hash_sha256`,
  all 30,507 masters) that v3 lacks — v3 has a sha256 for only 11,333 of 34,167 files — and the MU
  sidecars are keyed by exactly that v4 hash. So v4 **is** in the live path for identity. It becomes
  dispensable only if someone backfills `sha256` into v3's ~23k missing files. Also read `ref_bp_*`
  from it (Beatport reference).
- **The brain** = a **Supabase (PostgreSQL) database** named **taghag**. This is the
  similarity / DJ-mixing engine. **It is currently almost empty. Populating it is the priority.**
- **content_sha256** = a hash of the *entire FLAC file*. Used today as the identity key, but it
  is **unstable**: it changes every time any tool writes a tag or cover art into the file.
- **streaminfo_md5** = a hash of the *audio samples only* (from the FLAC STREAMINFO header). It
  does **not** change when tags/art are written. **This is the identity key you should use** (see §D).
- **The seam** = the join that links a real file → its identity → the brain's analysis rows.
- **The spine** = an append-only log of cross-session decisions: `shared/handoffs/handoff.jsonl`.
  **Never hand-edit it.** Append only via the tool `shared/bin/handoff-append`.
- **The ledger** = the locked-decisions file: `shared/decisions/DECISIONS_LOCKED.md`.
- **ref_bp_*** = Beatport reference tables (genre, BPM, artist, collaboration graph) living in v4/slut.
- **Nature gate / "the pool" / #50** = the rule that decides which tracks are DJ-mixable vs
  listening-only. Documented in `hag/docs/automix/POOL_DEFINITION.md`.
- **Anna's Archive (AA)** = an offline Kaggle dump of Spotify metadata. Used to bridge track
  identity across providers (spotify_id ↔ ISRC) and to build an artist collaboration graph.
- **REM** = the operator's personal memory system (separate from this project). A markdown store.

---

## B. File map — exact locations

**Repos & databases**
- Repos: `~/Projects/tag/hag/` and `~/Projects/tag/slut/`
- Shared coordination: `~/Projects/tag/shared/`
  - Ledger: `~/Projects/tag/shared/decisions/DECISIONS_LOCKED.md`
  - Spine (append-only log): `~/Projects/tag/shared/handoffs/handoff.jsonl`
  - Append tool: `~/Projects/tag/shared/bin/handoff-append`  (usage: `handoff-append --from hag --to slut --kind note --summary "..."`)
  - Current-truth snapshot: `~/Projects/tag/shared/STATE.md`
- Databases: `~/Projects/tag/slut_db/FRESH_2026/music_v3.db`  and  `.../music_v4.db`
- **Supabase brain:** project **taghag**, id `rnscghanqopewyfxqjhp` (ACTIVE, region ap-southeast-2).
  The other project `taglsut` / `hqirwdvflxnfeagejnjg` is a dead duplicate — ignore it.

**Scripts (all under the repos)**
- Redirect-gate fix (edited, uncommitted): `slut/tagslut/cli/commands/intake.py` (function `_db_is_v3_intake_ready`)
- Its test (rewritten, uncommitted): `slut/tests/cli/test_stage_v3_redirect.py`
- Staging CLI (edited, uncommitted): `slut/tools/ts-stage`
- Cover-art tool (edited, uncommitted): `slut/tools/review/embed_cover_art.py`
- Apple-MU analyzer scan: `hag/tools/run_mu_scan.py`  → writes `hag/tools/apple_mu_analyses/<content_sha256>.json`. **⚠ THIS SCAN IS DEAD** — the last sidecar was written ~7h before this handover, so it stalled early: coverage is only 2,621 of 30,507 (newest sidecar 03:20), NOT running toward completion. **Restart it (`cd hag/tools && python3 run_mu_scan.py`, it skips finished ones) and let it finish** before the §E1 `apple_track_analysis` ingest has any real data — right now that step loads almost nothing. Verify the true count first: `ls hag/tools/apple_mu_analyses/*.json | wc -l`
- Spotify audio-analysis fetch: `hag/tools/fetch_automix_payloads.py`  → writes `<spotify_id>.json` payload files.
  - Payloads exist in **both** `hag/automix_payloads/` (the main store, ~27k files) and `hag/tools/automix_payloads/` (7,877). Together ≈26,562 real analyses — roughly the whole fetchable universe. **Count them with `find <dir> -name '*.json' | wc -l`, NOT `ls *.json` — the main folder has too many files and `ls *.json` overflows the shell and falsely returns 0.** When fetching, pass an absolute `--out`.
- Beatport reference ingest: `slut/tools/v4/ingest_beatport_reference.py`, `slut/tools/v4/promote_artists.py`
- Anna's-Archive / Spotify ingest: `slut/tools/v4/ingest_spotify_reference.py`, `slut/tools/v4/aa_parquet_to_sqlite.py`, `hag/tools/build_spotify_isrc_bridge.py`

**Data artifacts (outputs from this session, all in `~/Projects/tag/`)**
- `genre_trust.csv` — every track tiered by how trustworthy its genre is.
- `needs_mik_rbx_analysis.m3u` — 30,507 master files to run through MIK / Rekordbox.
- `spotify_ids_last_batch.txt` — remaining Spotify IDs to fetch.
- `hag/tools/math.txt` — the Spotify-fetch reconciliation notes.
- Prior handover (Claude-oriented): `~/Projects/tag/HANDOFF_NEXT_OPUS_20260705.md`

**External data & credentials**
- Anna's-Archive Spotify dump: `/Volumes/ATTIC/kaggle-data/spotify-aa/` (`tracks.parquet`, `artists.parquet` — note: `artists.parquet` has NO genre column, only name/followers/popularity)
- Beatport-10M Kaggle dump: `/Volumes/ATTIC/kaggle-data/10-m-beatport-tracks-spotify-audio-features/`
- Spotify API credentials: `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` in `hag/.env` (also present in `slut/.env`). These mint a **client-credentials** token — no browser needed — good for public artist/genre lookups.
- Music files: masters at `/Volumes/MUSIC/MASTER_LIBRARY/`, incoming at `/Volumes/MUSIC/staging/`
- MIK database (energy/key): `~/Library/Application Support/Mixedinkey/Collection11.mikdb`
- Pool/nature-gate doc: `hag/docs/automix/POOL_DEFINITION.md`
- Curated "listening-only" artist list (248 names): `/Users/g/Reference/tagslut-readonly/legacy/handover/iceberg-prompts-2026-06-10/fable_iceberg_prompt.md`

**Environment notes**
- Databases: open with plain `sqlite3.connect(path)` — **never** the `?mode=ro` form (it fails on this Mac's APFS volume).
- Real work needs the operator's Mac shell (the py3.14 environment, `/Volumes`, `~/.config`). A sandbox cannot see those.

---

## C. The direction (already recorded, but UNCOMMITTED)
v4 is **write-frozen but read as the SHA source** (see §A — it is load-bearing for the seam, not
dispensable), v3 stays operational, and the Supabase brain is the priority. A prior session wrote
this into the ledger as `DECISIONS_LOCKED §15 addendum` and the nature-gate ratification as `§16`,
and closed spine `#50` with entries `#68`/`#69`. **These edits are not yet `git commit`-ed.** Verify
they're present, and if the §15 addendum implies v4 is "inert / out of the path," correct it — the
brain depends on v4's `file_hash_sha256`. Commit when the operator says so.

---

## D. CRITICAL — the identity key for the seam (ground truth from the instance that tried it)
Getting the join key right is the whole ballgame, and the last session found the exact trap by reading the code:
- The Apple-MU sidecars `hag/tools/apple_mu_analyses/<hash>.json` are named by **v4's `track_file.file_hash_sha256`** — because `run_mu_scan.py` reads that column. So the sidecar key = v4's whole-file SHA-256.
- **v3 has poor SHA coverage:** its `files` view holds 34,167 FLACs, but only **11,333 have `sha256`**; the other **23,456 have only `streaminfo_md5`**.
- **v4 has full coverage:** `file_hash_sha256` for all **30,507** masters.
- The existing ingest script **`extract_dj_slice.py`** (psycopg2) keys `audio_file` on `file_key="streaminfo:X"` for the 23k v3 files that lack sha256, and never sets `checksum_sha256`. But the sidecar lookup expects `file_key="sha256:{sha256}"`. **These two keys don't match → the join silently finds nothing.** This is the whole reason the brain looks empty even where analysis exists.

**Immediate fix:** build `audio_file` keyed on **v4's `file_hash_sha256`** (reading v4 is allowed — it's frozen for *writes* only). That matches the sidecar names *and* covers all 30,507 masters. Join to v3 **by file path** to pull the canonical metadata.

**Separate, longer-term concern — do NOT block on it:** any whole-file SHA (v3's or v4's) drifts when the operator tags a file (MIK/cover-art writes rewrite the bytes). The tag-stable identity is `streaminfo_md5` (audio-only hash). Re-keying the seam + renaming sidecars to `streaminfo_md5` is a future hardening task (spine `#66`/`#67`). For the *first* ingest, use v4's `file_hash_sha256` so the sidecars actually join — then harden later.

---

## E. Pending work (each item: what it is → where → next step)

1. **Populate the Supabase brain (PRIORITY).** It has 19 tables, all empty except `track_embedding`
   (744 orphaned rows). The identity table `audio_file` (keyed on the hash — use `streaminfo_md5` per §D)
   is empty; everything else joins to it via `audio_file_id`. Steps: fill `audio_file` from the ~30,507
   masters → ingest `apple_track_analysis` from `hag/tools/apple_mu_analyses/*.json` → `dj_tag` from MIK
   energy + cleaned genre → `track_analysis` from Essentia when ready → re-attach the 744 embeddings.
   Bulk-load via the Supabase service key in `hag/.env` (psycopg2 / COPY), not row-by-row.

   **Existing tooling and its traps (read the code before reusing it — from the last session):**
   - **`extract_dj_slice.py`** already writes `audio_file`/`dj_tag` via psycopg2 — but it keys on `streaminfo:X`
     for the 23k v3-no-sha files and never sets `checksum_sha256`, so its rows won't match the MU sidecars (see §D).
     Point it at v4's `file_hash_sha256`, or replace it.
   - **`run_apple_music_ingestion()`** is a **live analyzer** (it calls the Swift binary and recomputes the SHA from
     disk). It is **NOT** a sidecar reader — do not use it to load the existing `apple_mu_analyses/*.json`.
     Write a **separate Phase-1 script** that *reads the sidecars* and inserts `apple_track_analysis` rows.
   - **`mik_xml_adapter.py`** is for single lookups, not bulk ingest.
   - **Recommended shape:** one **Phase-0** script that reads v4 (for `file_hash_sha256`) + v3 (for canonical
     metadata), joins them **by file path**, and writes `audio_file` + `dj_tag` in a single pass; then a
     **Phase-1** script that reads the MU sidecars into `apple_track_analysis`. (The Beatport/Spotify reference
     ingest — "Part B" — is slut-repo work, run it in the slut context, not hag's.)

2. **Genre / metadata clean.** `~/Projects/tag/genre_trust.csv` tiers all tracks. Fix bad genres with:
   Beatport (`ref_bp_track`, authoritative for ~14k) → Spotify artist-genre (client-creds token from §B,
   proven working) → Essentia measured-genre (for artists Spotify returns empty). The blanket-"House"
   mislabel is a known older bug that was only half-fixed on an old DB.

3. **Naming template (the operator's original ask — do this early).** Rename master files so the track
   number sorts correctly by filename. This is a filename-template change at promote time in slut — a
   small, file-only change. **Confirm the exact desired format with the operator and preview on ~10 files
   before touching the library.** Needs no v4 or Supabase.

4. **Nature gate + listening-artists.** The ratified rules are in `DECISIONS_LOCKED §16` and
   `POOL_DEFINITION.md`. Then wire the 248-name listening-artist list (§B path) into the "reject" signal —
   but Beatport/playlist presence must override it (≈320 listening-artist tracks are legitimately DJ tracks).

5. **Anna's Archive artist-relationship graph.** AA builds artist entities + an artist-artist collaboration
   graph (via `ingest_spotify_reference.py` + `aa_parquet_to_sqlite.py`). The Beatport version is done
   (6,470 artists); the AA version is tooled but never run. Note: **the Supabase brain has no artist or
   relationship tables at all** — decide whether to add them so this graph lives where the brain can use it.

6. **Commit the four fixes** in §B (redirect gate + its test, the ts-stage `qobuz-dl` mapping, the cover-art
   fix). All tested, on branch `dev`, uncommitted.

7. **REM index (low priority, operator's personal system).** All session transcripts are safely captured in
   `~/Library/Mobile Documents/com~apple~CloudDocs/Claude/Projects/Projects/rem/masters/`. Its derived index
   (`normalized/records.jsonl`) was accidentally shrunk (36,768 → 90) because REM's `normalize` step only
   parses the "distilled" source, not the raw `claude-code`/`cowork` logs. Recover by either restoring that
   file from iCloud version history, or fixing `rem/bin/rem.py`'s normalize to parse the raw session `.jsonl`.
   **The masters (truth) are intact — nothing is lost, only the index.**

---

## F. Rules
- Never hand-edit the spine; use `handoff-append`. Never write to v4. No `?mode=ro`. Verify inherited
  numbers before trusting them. Cite file paths for every claim. The operator wants two things: a
  clean, correctly-named library, and the mixing brain — don't add anything that serves neither.
