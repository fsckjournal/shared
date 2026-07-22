# HANDOFF — 2026-07-12 pm

## 🔴 LIVE / URGENT: automix pool is empty (0 tracks)
- `hag/build_pool.py` → **Final pool size 0**. Cause (confirmed, advisor-reviewed):
  the **agent-run `#250` v4-native `dj_tag` feed (this morning, commit `887808a`)**
  upserted identity-only rows over the shared `dj_tag` store and **clobbered
  `tag_source='rekordbox_xml'`+`bpm`: 25,075 rows → 528.** The RXB-BPM gate
  (`tag_source LIKE 'rekordbox%'`) now finds ~nothing → empty pool.
- **Not** the crosswalk re-key fork (#257) — independent regression, from #3b's sibling
  feeder, already live. Pool worked through 07-08 (see `automix_pool.csv` 07-07,
  `Harmonic_Neighborhood_EliAndFur_7A.m3u8` 07-08).
- Confirming query already run: `dj_tag` GROUP BY tag_source → mik 28,321 / (null) 1,568
  / local_id3 1,319 / **rekordbox_xml 528** / mixonset 172.
- **FIX (needs operator GO — live Supabase write):** re-feed rekordbox bpm/tag_source
  into `dj_tag` from the rekordbox XML export **or** a pre-#250 `dj_tag` backup. #250's
  identity-only feed **cannot** restore them. `dj_tag` is one-row-per-file
  (`on_conflict=owner,audio_file_id`), so the re-feed must merge, not overwrite identity.
- Advisor agent (has full evidence chain): `a4107af95d51129e2`.

## Pool re-key (v3-kill blocker #3 half-B) — do NOT run the prompt as written
- `slut/docs/v4/PROMPT_pool_rekey_blocker3b.md` is **fenced/superseded** by spine `#257`:
  it is NOT read-only/mechanical. hag has no v4-native `spotify_track_id`; feeding the
  pool's spotify gate needs a **gated Supabase write**. `isrc`+`title` already v4-native.
- **Open fork (operator/advisor to pick):** (B) refresh `crosswalk_v3v4_identity` from
  `music_v4.db` in place, vs (C) write spotify into a v4-native hag table + re-key readers.

## Prompts written this session (`slut/docs/v4/`)
1. `PROMPT_pool_rekey_blocker3b.md` — FENCED (see above).
2. `PROMPT_q5_reproducible_build.md` — make `music_v4.db` rebuildable from repo (#1 priority).
3. `PROMPT_v4_native_seed_ts_get_wiring.md` — wire `ts-get --v4-native-seed` (run AFTER Q5).
- Batching: Q5 + (resolved) re-key are read/scratch-only → parallel-safe; native-seed
  writes the DB → run after Q5, never concurrent.

## Privacy (done)
- `shared/advisor/` untracked + gitignored (commit `c579c89`); files remain on disk;
  canonical advisor memory is `~/.claude/agent-memory/advisor/`. Sensitive memories
  (profiling/receive-questions) were in unpushed commit `4fb265f`, now **dropped — never
  pushed**. NOTE: `shared` is a **PUBLIC** GitHub repo; 16 older advisor files remain in
  public history (untracking HEAD doesn't purge past).

## ⚠️ Note for next agent
An **autonomous process is committing AND pushing to `shared`** (spine/STATE `#257`
commits `4025130`/`252a4da` were not made by this session). Expect the branch to move
under you; re-check `origin/master` before assuming a hash.
