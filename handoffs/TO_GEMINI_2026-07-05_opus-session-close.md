# Handover → Gemini

**From:** Opus session, 2026-07-05, closing because the operator (Georges) is about to hit a 24h rate limit and won't be reachable. Act on this in his absence, but stay inside the guardrails in §4 — he cannot approve new scope right now.

Read this top to bottom before touching anything. Every load-bearing claim is marked **[verified in code]**, **[operator's own words]**, or **[reverted — do not reinstate]**.

---

## 1. What this session REVERTED — do not put it back without the operator saying so

All of it was uncommitted working-tree cruft written by earlier agents and recorded as if the operator had decided it. He hadn't. Restored `shared/` to last committed state:

- `shared/decisions/DECISIONS_LOCKED.md` → restored to HEAD. **Removed** the §15 "v4 is **frozen**" addendum and the §16 "nature gate **RATIFIED**" block. Both were written as operator-decided; they were not.
- `shared/handoffs/handoff.jsonl` → restored to HEAD. Spine now correctly ends at **#65**. **Removed** entries #66–#71: the MASTER_LIBRARY hash-drift blocker (#66), the two "who mutated the masters" forensics notes (#67, #71), the #50 "RATIFIED" answer (#68), the v4-frozen note (#69), and the Anna's Archive scope note (#70).
- Fixed a **hand-injected corruption** inside committed entry **#61** — someone had jammed the sentence *"i think the anna's archive is the jackpot here…"* into the middle of that JSON line, mangling it. HEAD is clean; restored.
- Emptied `shared/handoffs/gemini-handover-supabase-ingest-2026-07-05.md`.

**Backups of everything removed** live at `outputs/reverted_shared_20260705/` (`DECISIONS_LOCKED.dirty.md`, `handoff.dirty.jsonl`, the gemini handover copy, and `reverted.diff`). **Cherry-pick from there ONLY on explicit operator instruction.**

---

## 2. The operator's actual words — stop twisting them

Three things earlier sessions distorted. Do not repeat these:

- **v4 status.** He said, verbatim: **"keep it if it won't become a burden."** [operator's own words] He did **not** say freeze it, did **not** call it inert doctrine, did **not** say Supabase is "the priority." v4 is conditionally kept, as-is. Do not write the word "frozen" anywhere.
- **The "small thing" he keeps asking for is the INTER-TRACK / ARTIST-ARTIST RELATIONSHIPS** — the Anna's Archive collaboration graph. It is **NOT** file renaming and **NOT** a metadata-cleanup chore. Earlier agents (including this lineage, twice) substituted "naming template" for his real ask; he corrected it flatly: *"i never said i wanted renaming… stop twisting my words."* [operator's own words]
- **Hashes are closed.** *"FUCK THE HASHES. IM NOT A ROBOT."* [operator's own words] Stop the hash-drift forensics and the blame-tracing. The `streaminfo_md5` identity-key proposal is **UNRATIFIED** — he explicitly declined to engage it. Do not treat it as decided, do not pursue it unless he reopens it himself.

---

## 3. The one real task (verified against code, trustworthy)

The relationships he wants are tooled but never executed:

- **Beatport** artist + collab graph: **DONE** — 6,470 artists, `ref_bp_collab` derived. [verified in code]
- **Anna's Archive (Spotify-AA)** artist + collab graph: **TOOLED, NEVER RUN.** Pending the `promote_artists` (Spotify-AA) pass. [verified in code: `slut/docs/v4/SPRINT_STATUS.md:46-50,104`]

Pipeline (three steps):
1. `slut/tools/v4/aa_parquet_to_sqlite.py` → emits `aa_slice.sqlite` (resolves each track's artists into an `artist_ids` JSON array from the AA parquet's `track_artists` + `artists` tables).
2. `slut/tools/v4/ingest_spotify_reference.py extract` → ATTACHes the slice, ISRC-joins to the v4 library, builds `ref_spotify_track` / `ref_spotify_artist` / `ref_track_artist` **and derives the artist entities + co-credit collaboration graph** — same `(artist_a, artist_b, weight)` shape as Beatport's `ref_bp_collab`: an edge whenever two **non-remixer** artists share a track, weighted by shared-track count. The 148GB giant parquet is discarded after the slice.
3. `slut/tools/v4/promote_artists.py` → promotes the ref layer into first-class `artist` + `track_artist` tables (Beatport already done; Spotify-AA is the pending half).

Inputs / environment:
- AA Spotify parquet: `/Volumes/ATTIC/kaggle-data/spotify-aa` (`tracks.parquet`).
- v4 DB: `~/Projects/tag/slut_db/FRESH_2026/`.
- **Requires Desktop Commander** (the operator's real py3.14 env / `/Volumes` access). A sandbox cannot see `/Volumes`.
- Separate, optional second source noted in the "Grand Heist" record: Spotify `GET /v1/artists/{id}/related-artists` API — distinct from the offline co-credit graph. Later, not now.

---

## 4. Directive — do the work, not the paperwork

- **Run the Spotify-AA artist/collab-graph pipeline** (§3) if Desktop Commander + `/Volumes/ATTIC` are available. It's additive and non-destructive — it builds ref/artist tables and discards the parquet; it does **not** touch masters. Have the actual **artist-artist edges** ready for the operator when he's back.
- **DO NOT append to the spine. DO NOT add `DECISIONS_LOCKED` lines. DO NOT amend #70.** He spent this entire session tearing exactly that out. No ledger edits about this work unless he asks in his own words.
- **DO NOT touch master files. DO NOT run any re-hash or hash-drift analysis.**
- **DO NOT invent new scope** while he's rate-limited (~24h). The Supabase-populate plan, the nature-gate ratification, LISTENING_ARTISTS, the naming template — treat all of those as **agent proposals, not his asks.** None are ratified.
- When you report back: quote **verified vs. assumed** explicitly. Never write "ratified" unless he ratified it himself.

He wants his music and the relationships between the artists in it — as real, queryable data. That's the whole job. Build that; leave the bookkeeping alone.
