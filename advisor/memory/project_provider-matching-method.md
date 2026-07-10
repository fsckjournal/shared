---
name: provider-matching-method
description: Georges's proven method for linking owned masters to Beatport/Spotify/TIDAL provider IDs — the Lexicon export bridge + duration-as-tie-breaker matching
metadata:
  type: project
---

Linking v4 owned masters to provider IDs (Beatport/Spotify) — the operator's proven pipeline, used 2026-07-10 to close the Beatport/Spotify ref gap (`ref_bp_track` 15,975→17,500; `ref_spotify_track` 22,882→24,241; spine #158).

**The bridge = Lexicon, not the API.** Inject gap tracks as a Lexicon playlist → **Save-to-Beatport / export-to-Spotify** → the exported CSV carries the provider's **native ISRC + provider ID**. One hop, strict, no Soundiiz round-trip. This is how the prior +5,756 backfill (#61) was built too. Give the operator an **M3U of the still-unmatched owned masters** (`membership='mix'`, present on disk) as the input; he runs the export loop and hands back `My {Beatport,Spotify,TIDAL} Library-*.csv` (cols: Track name, Artist name, Album, Playlist name, Type, ISRC, `<provider> - id`).

**Two match modes:**
- **Exact** — our `track.isrc` == export ISRC. Safe, direct fill. (Beatport via `catalog_list_tracks({isrc})` API for numeric IDs; Spotify direct-insert from the export's spotify_id, no API.)
- **Identity recovery** — same recording under a *different release ISRC* ("these are the same tracks; your search is too strict"). Match by **artist + title**, then **CONFIRM BY DURATION** — operator: *"the tie-breaker is the duration."* ±2s (API) / ±1s (offline). Duration both disambiguates multiple same-title versions AND rejects wrong mixes (Extended vs Radio have different lengths).

**Why:** exact-ISRC alone misses ~half the owned matches because a recording carries multiple ISRCs across releases (compilation/remaster/region). But naive title matching false-positives ("Another Station"≠"As If No One Is Here", same artist+duration) and version-confuses ("Al-Furat Extended" vs "Original", same duration). Duration + mix-field is what makes it precise.

**How to apply:**
- **Beatport puts the mix name in a SEPARATE `mix` field; v4 embeds it in the title.** So bare title-core over-collides — strip parentheticals/`- suffix` from the v4 side, and use the mix field to disambiguate. This is the recurring Beatport gotcha ("the mix name is in the mix field").
- Best offline source: a Lexicon export with flac + streaming rows **sorted by name** (`~/Music/allthree.csv` shape: title,artist,album,duration,mix,location). A flac row + a streaming row (`spotify:/tracks/` or `beatport:/tracks/` in `location`) with **matching duration** = a match. flac→v4 by path (exact); streaming→provider ID. Unambiguous-only; ~99.7% of duration-matches are unambiguous.
- Store `ref_bp_track` keyed by OUR ISRC (closes the `track.isrc` join); Beatport's real ISRC optionally recorded as a `track_alias` (provider='beatport') for provenance. Rows can be minimal (bp_id + title + mix + bpm-if-known, numeric IDs NULL) — consistent with the many NULL-ID rows already there.
- The **not-owned** export ISRCs (verified absent from every v4 store: `track.isrc`, `library_track_sources`, `files` husk, `track_alias`) are the **acquisition wishlist**, not hidden closure — set aside, don't fuzzy-force.

See [[radical-collapse-and-hazards]] (two-store disease — always check ALL ISRC stores before calling something "not owned").
