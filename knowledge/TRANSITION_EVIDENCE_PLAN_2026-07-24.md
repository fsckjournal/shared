# Transition-Evidence Plan — v2 (2026-07-24)

**Status: settled design, operator-confirmed 2026-07-24 ("update the plan"). Supersedes the
ListenBrainz-primary approach embodied in the untracked extractor
`slut/.claude/worktrees/v3-kill-failclose/tools/transition_edges_extract.py` (kept, not deleted —
preserve-don't-purge; do not run it as-is for edge production).**

Scope: how playback/playlist evidence becomes transition edges for the automix engine.
Lane note: edge *scoring/consumption* is hag's lane; the identity join feeding it is slut's;
this plan itself is an operator-level design spanning both — filed to the spine from a lane
only because `handoff-append --from` has no operator value (see spine #163).

Provenance: evidence figures below are from the 2026-07-23/24 Codex evidence sessions
(operator-relayed 2026-07-24). Figures marked `[inherited]` were not re-derived in this session;
re-derive before promoting any of them into a deliverable. The three extractor flaws marked
`[verified]` were confirmed in code this session (file:line cited).

## 1. Evidence corpus (what actually exists)

- Spotify lifetime export: 123,114 audio records / 122,880 track events, Jan 2012–Mar 2026. [inherited]
- Two Account Data ZIPs are **different Spotify identities**: `Spotify Account Data 2` matches
  97.3% of the overlapping one-year lifetime records; the other matches 0%. **Never merge them.** [inherited]
- Matching account: 510 playlist sequence snapshots, 58,603 directed playlist edges. [inherited]
- Soundiiz corpus (`/Users/g/Downloads` + `/Users/g/Downloads/soundiiz`): 24 hash-distinct
  Spotify-library CSVs; 563,719 rows with Spotify IDs; 101,716 distinct track IDs; 94,033
  unambiguous Spotify-ID→ISRC mappings (exactly 1 conflicting ID). Largest:
  `My Spotify Library-18.csv` — 444,616 rows, 99,769 IDs, 671 playlists, 273,314 directed
  playlist edges. [inherited]
- `CATALOG_enriched_union.csv`: 31,884 rows with Spotify ID + ISRC + local FLAC path; 25,336
  exact-match active v4 archive-master paths. [inherited]
- Strict event coverage into v4 after requiring unique mappings + agreement of direct alias,
  exported ISRC, and exact path: **3,440 history IDs / 32,516 events / 26.46%** — supersedes the
  earlier 20.64% (Spotify-ID→ISRC bridge only) and 17.59% (direct alias only). [inherited]
- Playlist order predicts real playback: recent non-shuffle transitions follow saved playlist
  order 22.28–23.26% forward vs 1.86–2.10% reverse (lifetime-account vs Library-18 measures).
  This validates playlist order as intentional evidence. [inherited]
- No Technical Log ZIP found in either checked root; the 3 Spotify ZIPs = lifetime history + 2
  Account Data identities. [inherited]
- `flibrary 2.db` (/Volumes/ATTIC): historical FLAC inventory (26,566 FLACs, 22,203 MBIDs,
  16,498 ISRCs; snapshots Jan–Aug 2025; integrity ok). **Archival identity evidence only — never
  auto-import into v4.** [inherited]
- Mixonset/Offtrack `playhistory.txt`: 769 played rows May–Jul 2026, 155 Spotify tracks, 307
  explicitly-marked transition edges — machine-generated mixes from an operator-supplied pool,
  to be labeled as generated (not hand-authored) evidence. [inherited]
- Evidence limit: Spotify and ListenBrainz both start Jan 2012; iTunes XML has no historical play
  dates. The pre-2012 indie baseline is an **operator-known anchor**, not derivable from these
  exports. Do not claim to reconstruct it.

## 2. Why the v1 (ListenBrainz-primary) extractor is superseded

`transition_edges_extract.py` flaws — first three verified in code 2026-07-24:

1. Drops MBID-less events before sessionization (`if ts and mbid`, line 52) — can invent A→C
   across an unresolved B. [verified]
2. Arbitrarily takes the first ISRC when several exist (`v4.split(";")[0]`, line 34). [verified]
3. Removes all self-transitions (`pisrc != cur`, line 108) — kills repeat/pass-out detection. [verified]
4. ListenBrainz should be a corroboration source, not primary — Spotify's own export carries
   `ms_played`, shuffle, skip, and reason fields ListenBrainz lacks.
5. Raw recurrence overweights repeat loops and Spotify logging bursts.
6. Filtering edges by shared v4 release conflates release membership with playback context.
7. A single global recency coefficient cannot represent both the 2012 shift and the recent
   playlist-dominant regime.

## 3. The settled design (seven parts)

1. **Intentional lane:** deduplicated Spotify playlist order — the strongest prior.
   **Exclude utility/migration playlists** from intentional-transition training:
   `Offtrack Spotify Batch*`, `Beatport Gap Batch*`, `RBX_MIK`, aggregate/library dumps.
2. **Observed lane:** Spotify playback adjacency from the lifetime export, using timestamps,
   `ms_played`, shuffle, skip, and reason fields.
3. **Corroboration lane:** corrected ListenBrainz adjacency — unresolved events retained as
   adjacency *breakers*, never silently dropped.
4. **Artifact lane:** self-repeat runs and zero-duration bursts (576 zero-duration bursts, 14
   long-repeat candidates, 5 high-confidence continuous-repeat sessions identified) recorded for
   audit; the *initial selection* keeps its weight, subsequent repeats are excluded from edge
   reinforcement. Generated mixes (Mixonset `playhistory.txt`) are labeled generated, not
   hand-authored.
5. **Era model:** separate 2012-transition, middle-history, and recent playlist-dominant regimes —
   no single global decay.
6. **Identity ladder:** direct Spotify alias → Spotify-ID/ISRC bridge → unambiguous
   metadata/ISRC bridge → **explicit unresolved external node** (unresolved events never
   disappear).
7. **Scoring:** session-capped support, provenance retained on every edge, playlist evidence
   weighted above passive plays.

## 4. Execution sequence (identity join first — the duration gate was premature)

The paused duration gate ran downstream of the small `export_soundiiz.csv` (29,324 rows /
18,016 ISRCs); its 2,979 unresolved rows are **not** the correct review queue. Correct order:

1. Rebuild the identity join from ALL hash-deduplicated Spotify-ID/ISRC exports (24 files).
2. Incorporate the exact-path `CATALOG_enriched_union.csv` bridge.
3. Regenerate the unresolved cohorts.
4. Only then rerun duration gating on the true residual candidates.
5. Then build the v2 edge extraction per §3.

## 5. Hard constraints (unchanged, restated)

- All work read-only on the exports; any v4 write goes through slut's single-writer path (§5 of
  DECISIONS_LOCKED) on a gated copy. Never delete masters.
- The two Spotify Account Data identities are never merged.
- `flibrary 2.db` is evidence, not an import source.
