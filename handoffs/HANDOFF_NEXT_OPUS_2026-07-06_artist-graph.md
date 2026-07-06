# Handoff — artist graph + nature-gate decisions, 2026-07-06 (PM)

Boot doc for the next session. Everything below was applied/verified live this session against the
taghag brain (Supabase `rnscghanqopewyfxqjhp`) and `slut_db/FRESH_2026/music_v4.db`. **Reproduce; do
not inherit on faith.** Spine arc: **#92–#96** (`tag/shared/handoffs/handoff.jsonl`).

## Direction locked this session (READ FIRST — DECISIONS_LOCKED)

1. **§15 REVISED (spine #96): v4 is now INERT / OUT OF THE RUNTIME PATH** — frozen, not fed, not
   deleted. Supabase (taghag) is the brain and **populating it is the active priority.** The brain no
   longer reads `music_v4.db` live; it bridges to v3 identity through `crosswalk_v3v4_identity`
   (loaded spine #87) keyed on the **content hash**, not path. ⚠️ `v3.content_sha256 ≠
   v4.file_hash_sha256` (~9% overlap, `IDENTITY_KEY_AND_MU_INGEST`) — bridge via the crosswalk's
   retag-stable keys (ISRC / `v3_streaminfo_md5`), do **NOT** re-key the brain to v3 full-file SHA.
2. **Nature gate item 16 AMENDED (spine #95): DJ-playlist/Rekordbox membership is REMOVED** as both a
   LISTENING_ARTISTS override and a positive DJ signal (operator, repeatedly: "i know what's in
   rekordbox"; corroborated — Rekordbox is 59.2% unmatched / 0 rows at MASTER_LIBRARY, POOL_DEFINITION
   §6, and the override was never computed). **Beatport presence is NOT an override** (operator) —
   supersedes the HANDOFF_2026-07-05/06 "Beatport/playlist wins, ~320 protected" framing; those ~320
   go to the iceberg. **LISTENING_ARTISTS override set is now `remix/extended` + `admitted` ONLY.**
   `fable_iceberg_prompt.md` signal 1 (DJ-playlist "decisive") is retired.

## What is DONE this session (verify — do not trust)

The artist layer landed in the brain (was: zero artist/relationship tables — the whole graph lived
only in frozen v4). Live counts (PostgREST, `?select=*` + `Prefer: count=exact`):

| Table | Count | Notes |
|---|---|---|
| `artist` | **13,191** | mirror of v4 `public.artist`; unifies beatport+spotify ids; **135 variant-spelling aliases folded** (Sven Väth→Vath, Beyoncé→Beyonce…) |
| `track_artist` | **41,608** | roles primary/feat/remixer; `audio_file_id` resolved via crosswalk; **1,431 skipped** (tracks not in brain `audio_file` — the #86 drift) |
| `artist_collab` | **15,226** | undirected, `artist_a<artist_b`, source-tagged: spotify 12,791 (co-credit) + beatport 2,435 |

Also live: `audio_file` 31,383 · `apple_track_analysis` 19,819 · `dj_tag` 30,954 · `crosswalk_v3v4_identity`
30,507 · `track_analysis` **440** · `track_embedding` **744**. DB size **361 MB / 500 MB** (~139 MB free).

Migrations applied (via `supabase db push`, hag repo, all committed + pushed):
- `20260707120000_add_artist_collaboration_graph.sql` — artist/track_artist/artist_collab (commit `12a5663`).
- `20260707130000_add_roon_artist_views.sql` — `v_audio_file_artists`, `v_artist_collaborators` (commit `b4ec186`).

Code (hag `main`, committed + pushed):
- `tools/similarity/artist_affinity.py` + `crates.py --artist-aware` — opt-in artist-relationship
  re-rank for automix crates (same-artist/shared-credit penalty, collaborator/remix-lineage reward,
  clamped so sonic distance dominates). Pure scoring unit-tested, `tests/test_artist_affinity.py`
  **8 passing**. Commit `5b7b695`. **Default off** — existing pipeline untouched.

Loaders (idempotent, re-run picks up new artists/edges + backfilled `audio_file` rows):
- `outputs/load_artist_graph.py` — full mirror (v4 → brain, REST upsert).
- `outputs/fold_aliases_supabase.py` — brain-only alias fold (delete losers via FK cascade + upsert
  folded graph). `--apply` to run; dry-run default.

## Open work — priority

1. **[BLOCKED on operator] LISTENING_ARTISTS wiring (brain-side).** Flag the roster on `artist`
   (deduped) so automix/pool excludes them; override = `remix/extended` + `admitted` only (per item 16).
   Blocker: **which roster** — the ~240 in `fable_iceberg_prompt.md`, or that minus the
   Arabic/Lebanese/Turkish names `slut/tools/filter_listening_artists.py` strips (Fairuz, Oum Kalthoum,
   Ziad Rahbani…). Do brain-side, NOT v3 `dj_admission` (v3 corrupt + brain = priority).
2. **[parked behind #86] 1,431 skipped `track_artist` edges** — tracks not yet in brain `audio_file`.
   The sibling session's v3 reconcile (RELOCATE moved rows / DELGONE only genuinely-gone) fixes the
   ~1,450 drift; once it lands, re-run `load_artist_graph.py` (idempotent) and they resolve.
3. **The real pool gap: Essentia.** `track_analysis` 440 + `track_embedding` 744 → the usable automix
   pool is ~236–440 tracks, not 30k. Background job; not forceable from a cowork session.
4. **[slut lane, spec'd] v4 artist alias merge** — `slut/tools/v4/merge_artist_aliases.py` (uncommitted)
   folds the same 135 aliases in v4 if v4 should match the brain. Prompt: `PROMPT_artist_alias_merge_2026-07-06.md`.
5. genre clean (`genre_trust.csv` ladder) · naming template (operator's original ask, file-layer) ·
   commit the 4 slut `dev` fixes · background jobs (MIK energy, Apple MU scan, Rekordbox on Normal —
   turn off its key-ID3 write).

## Coordination / do-nots

- **A sibling session is actively fixing `music_v3.db` corruption + reconcile.** Stay out of v3. The
  brain↔v3 bridge is hash-based (crosswalk), insulated from their path relocations.
- **Do NOT touch the `audio_file` re-sync/#86** — operator-deferred ("not gonna make a difference").
- **v4 is inert** (§15/#96) — don't write it; the brain-only alias fold means v4 still carries the 135
  aliases (divergence is intentional; brain is the deduped source for automix/Roon).
- Shared tag repos block raw `git commit` — use `~/Projects/tag/shared/bin/git-safe commit -m … <paths>`.

## Key artifacts

- `shared/knowledge/SUPABASE_RESUME_2026-07-07.md` (connection facts, tooling, CLI reconcile procedure).
- `shared/knowledge/artist_alias_candidates_2026-07-06.csv` (307 merge pairs + group/member keeps).
- `shared/handoffs/PROMPT_artist_alias_merge_2026-07-06.md` (v4-side fold spec).
- Spine: #92 (artist graph mirrored), #93 (alias-merge ask), #94 (alias fold brain-only),
  #95 (item 16 override amend), #96 (§15 v4-inert / brain-priority).
