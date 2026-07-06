# PROMPT — Artist entities + collaboration graph into the taghag brain

Self-contained handoff for a fresh session. Goal: give the brain an **artist layer** — artist
entities + an **artist↔artist collaboration graph** (co-credit + remix lineage) — so similarity /
ordering can use "who made this with whom." Verify every number below live; don't inherit on faith.

## Why this is new
The taghag brain (Supabase `rnscghanqopewyfxqjhp`) has **zero artist or relationship tables**
(verified 2026-07-06 — the whole relationship layer lives only in v4/slut). The recap's north star:
*model artist + relationship tables where the brain can consume them.*

## What already exists (prior art — do NOT rebuild)
- **Beatport graph — DONE, in `music_v4.db` (slut).** Migration `slut/tagslut/storage/migrations/0019_adopt_ref_beatport_layer.sql`; builder `slut/tools/v4/ingest_beatport_reference.py`. Coverage: **6,470 artists / 26,167 artist-track edges / 1,612 labels / 2,435 collab edges**; `bp_artist_track(artist_id, track_id, is_remixer)` carries **remix lineage**; `track_artist(role = primary/feat/remixer)` = 15,771 links (spine #57, `docs/v4/SPRINT_STATUS.md`).
- **Spotify / Anna's-Archive graph — TOOLED BUT NEVER RUN.** `slut/tools/v4/ingest_spotify_reference.py` creates `ref_spotify_track / ref_artist / ref_track_artist / ref_artist_collab(artist_a, artist_b, weight)`. Per `shared/handoffs/gemini-handover-supabase-ingest-2026-07-05.md:526`: *"Spotify-AA layer: tools written, parquet downloaded, never executed."* `ref_spotify_track` is partially loaded (~23,312 / 76% ISRC bridge). `slut/tools/v4/promote_artists.py` exists too.

## Source data (on ATTIC — verified 2026-07-06)
`/Volumes/ATTIC/kaggle-data/` (47 GB):
- **`spotify-aa/`** — `artists.parquet`, `track_artists.parquet`, `tracks.parquet` = **the AA/Spotify graph source** (`ingest_spotify_reference.py`'s input; this is the "parquet downloaded, never executed"). `track_artists.parquet` is the co-credit edge source; artist role/remixer must be derived from it.
- **`10-m-beatport-tracks-spotify-audio-features/`** — `bp_artist.csv`, `bp_artist_track.csv`, `bp_label_artist.csv`, `sp_artist.csv`, `sp_track.csv`, … = the Beatport-graph source (already ingested via `0019`); useful for the cross-provider artist unify.
- `track_audio_features.parquet` (14 GB) = Spotify **audio features** for ~10M tracks — an *audio* layer, NOT graph data; ignore for this task.

## Not the graph source
`hag/automix_payloads/` (31,822 json / 18 GB) are Spotify **audio-analysis** payloads
(tempo/key/segments/timbre) — the graph source is the AA parquets below, not these.

## Lane split (critical — v4 is write-frozen, §15)
- **Building the graph in v4 = slut lane.** `music_v4.db` is write-frozen (§15); `ref_*` layers land only via **deliberate slut action / migration** (that's how Beatport's `0019` was adopted). A prior *ad-hoc* Gemini write of `ref_*` to v4 was flagged as a single-writer violation (spine #54) — do it the sanctioned slut way, not ad-hoc.
- **Mirroring the graph into the brain = hag lane.** hag reads v4, models the brain tables, loads them.

## Approach
1. **[slut] Run the AA/Spotify reference build** (`ingest_spotify_reference.py`) against the downloaded parquet → `ref_spotify_track / ref_artist / ref_track_artist / ref_artist_collab` in v4, via the sanctioned migration path (mirror `0019`). **Unify with the Beatport graph** — same artist under Beatport + Spotify ids and name-norm should be ONE entity; don't duplicate.
2. **[hag] Model brain tables** (Supabase): `artist(id, name_norm, spotify_id, beatport_id, …)`, `track_artist(audio_file_id ↔ artist_id, role)`, `artist_collab(artist_a, artist_b, weight, evidence)`. Join to the brain's `audio_file` via ISRC → `crosswalk_v3v4_identity` / `ref_spotify_track`. **Store entities + edges only, never raw payloads.**
3. **[hag] Load** via REST + service key (`hag/.env` `TAGHAG_SUPABASE_SECRET_KEY`) — the MCP is intermittently down. Idempotent upsert.
4. **Verify:** artist count, edge count, 0 orphan FKs, size delta vs the free-tier **166 MB headroom** (334/500 MB, spine #88 — edges are small, but check), and spot-check a known remix's `remixer` edge + a known collaboration.

## Gotchas
- **v4 write-freeze** → the v4 build is a slut-lane, migration-gated action, not an ad-hoc write (#54).
- **Artist name normalization** — the same artist appears under variant spellings/features across providers; unify on name-norm + provider ids or you'll double the node set.
- **Free-tier storage** — edges are tiny, but `apple_analysis_runs` (108 MB) + `track_cue` (77 MB) already eat 55%; confirm headroom before load.
- **MCP flaky** → REST/PostgREST with the service key, or the Supabase CLI (`hag/supabase`). See `SUPABASE_RESUME_2026-07-07.md` "CLI reconcile procedure."

## One decision to get from the operator first
Is the artist graph **canonical in v4 (slut) with the brain mirroring it**, or is **the brain the
primary home**? The recap says "so the graph lives where the brain can use it" (brain = consumer),
but the tooling builds in v4. Confirm the home before building tables in two places.

Spine arc to cite: #54 (v4 single-writer), #57 (Beatport ref adopted), #74/#87 (crosswalk/ISRC bridge).
