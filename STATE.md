# STATE — current truth, both repos (read this FIRST)

> **Boot: read `shared/OPERATOR.md`** — how to work with Georges (believe his reports, verify, move-dont-menu, never delete masters, collapse-dont-reconcile).

**This is a snapshot of what is true NOW, not history.** The log
(`handoffs/handoff.jsonl`) is chronological events; this file is the reconstructed
current state so a fresh session (or the operator) does not have to walk the log.
Locked policy lives in `decisions/DECISIONS_LOCKED.md`. **Update this file at the end of
a session; use the log only for events the other side must act on.**

Last updated: **2026-07-10** by slut (RADICAL COLLAPSE membership FULLY RULED+APPLIED mix/listen/unclassified + Fork1 alias LANDED on real v4 — see 🟢 block)

---

## 🟢 2026-07-10 — RADICAL COLLAPSE: membership FULLY RULED+APPLIED (mix/listen/unclassified) + Fork1 alias LANDED on real v4 (spine #148/#149)
Split re-verified EXACT vs 07-09: MASTER 25649 / ICEBERG 4695 / BOTH 0 / NEITHER 1101 (31445). #116 "5741 missing" = drain+off-disk, NOT corruption. Purple was NOT a ghost-contradiction — **#135**: real tags (#107) consumed by the MUSIC→ATTIC drain, curation now = LOCATION (#133 closed).
- **MEMBERSHIP — ✅ APPLIED to real `music_v4.db`** (`apply_membership_v2.py --apply`; #134 enum + #140 rule). Enum = **`mix` / `listen` / `unclassified`** (work/iceberg RETIRED as VALUES per #134; mix===work, listen===iceberg). 6089 DISAGREE resolved by **PRIMARY artist** (#140: primary∈listening→listen, else→mix — a feature must not drain a mixable track). **FINAL: mix 24529 / listen 4745 / unclassified 2171.** Reasons: mix_master 19560, feature_only_mix_140 4969, listen_location 4695, off_disk 1101, no_primary_140_unresolved **1070** (HELD — no primary link, `has_files_no_artist_link` #130 overlap, resolves free once artist links backfilled), primary_listening_140 50. Snapshots `music_v4.db.bak_pre_membership_20260710_093854` + `..._v2_20260710_094900`. Tools `slut/tools/v4/apply_membership_v2.py` (supersedes v1 vocab), idempotent/guarded.
- **FORK 1 alias — ✅ LANDED on real v4** (`apply_artist_alias.py --apply`, spine #149). `artist_alias(artist_id,alias,source,…)`, **69** folder aliases (#123 opt-a, #125 set; excludes Isolee/Pacific!/Slo). 0 orphans, idempotent. #123 CLOSED.
- **STILL PENDING:** downstream view regen + one-way Supabase mirror of the `mix` set (NOT regenerated — belongs to the going-forward capture / §15↔#113 v4-sole ratification); 1070 no-primary rows (free once artist links land); **Fork 2 key** (#144, hag-lane read-only: 206 mixed-cause, retarget `musical_key`→`key_camelot` + `0`→NULL unfreeze await hag+operator).
- **FORK 1 artist_alias** (`slut/tools/v4/apply_artist_alias.py`): new `artist_alias(artist_id,alias,source)` mirrors `track_alias`; **69** folder-string aliases loaded from `artist_tail_worksheet` (#123 opt-a, #125 set; excludes Isolee/Pacific!/Slo per #125). Option (b) folder-rename OUT.
- **FORK 2 measured-key** (`hag/tools/reconcile_mik_keys.py`, READ-ONLY re-run): **206** candidate drift reproduced (14846 raw, 98.6% notation), 4011 join-loss, 6126 same-row `musical_key`≠`key_camelot`. NOTHING written to brain.
- **AWAITS operator:** (a) #133 purple-vs-orange + MASTER-mass rule; (b) alias GO; (c) key column-retarget (`musical_key`→deprecate, `key_camelot` canonical) + `0`→NULL backfill GO. Scripts idempotent+guarded, dry-run default; real apply per item on GO.

---

## ✅ 2026-07-10 — ARTIST CHANGESET APPLIED TO REAL v4 (state, not plan)
`apply_artist_full.py` landed on real `music_v4.db` ~11:05 — mechanical relink (#119/#120: +245 relink / 970 demote) **+** credit-verified tail (#126: 1 merge + 5 VA + 7 mislink + Oum Kalthoum). **Real v4 is NO LONGER at baseline / NO LONGER "untouched"** — any doc below that still says so is superseded by this line.
- `track_artist` 43,240 -> **43,520** (+280) · `artist` 13,326 -> **13,333** (+7 = 8 created - 1 merged)
- Isolée = single row carrying **both** IDs (bp 7214 + sp 6FfT…); old Isolee row gone; Pacific!/Slo left split
- Guards passed (post-apply sha == target **64da87af**); idempotent re-run 11:13 confirmed no-op; 0 fk-orphans
- **NEW baseline `track_artist` sha = `64da87af`.** Old baseline `1d660dd3` is STALE — apply script now correctly refuses re-apply. Re-baseline anything gated on the old value.
- Spine: #128 (staged->**applied**), closes #120/#126/#128. Script committed slut@`0911918b` (dev).
- Advisor persona/memory relocated to mounted `shared/advisor/` (symlinked from ~/.claude), now version-controlled.

**Measured-key thread RESOLVED (2026-07-10, spine #132, READ-ONLY):** `reconcile_mik_keys.py` now reads BOTH `dj_tag` cols + normalizes to Camelot. `drift=14846` DISPROVEN — collapses to **206** candidate real-drift after `to_camelot()` (~98.6% notation artifact; 10-row dump proves each raw-drift row's own `key_camelot`==ZKEY). blob-scrape 33596/33596. `ingest_mik.py:88` `0`-sentinel guard LANDED (`_mik_key()`). NEW: `musical_key` vs `key_camelot` disagree 6126/22968 after norm (different ingest pass) -> treat `musical_key` deprecated; RPCs read `key_camelot` (206 drift). NO brain writes — 206 are mixed-cause candidates (#129 trap), `0`->NULL backfill frozen pending operator (open Q #132). Alias-capture fork = spine #123/#125 (69 pairs staged).

---
· Convention: slut maintains the slut section, hag the hag section; the shared header is either.

---

## ⚠ 2026-07-06 corrections (two fabrications killed — do not resurrect)
A Gemini/Opus handover (`HANDOFF_NEXT_OPUS_2026070*`, now archived) injected two items the
operator confirms he **never decided**:
1. **"v4 is inert / out of the path / brain joins v3 on `content_sha256`."** FALSE — **§15 stands**:
   v4 is *load-bearing for the identity seam*; the brain reads `v4.track_file.file_hash_sha256`
   because v3's SHA coverage is partial (verified 2026-07-06: v4 30,507 complete vs v3
   `content_sha256` 42,771/69,246). Operator defers on hash mechanics ("no opinion"). Do not re-key to v3.
2. **Naming/track-number template.** Operator: *"not a priority AT ALL"* (and earlier "i never said i
   wanted renaming"). Out of scope — stop re-listing it.

## Current focus (2026-07-06): populate the taghag brain — the SEAM IS ALREADY DONE
Verified live in Supabase (`rnscghanqopewyfxqjhp`): `audio_file` **31,383**, `dj_tag` **30,954**,
`track_cue` **371,198**, `track_embedding` 744. The real gap is **`apple_track_analysis` = 39** while
**~17,208 MU sidecars sit ready** in `hag/tools/apple_mu_analyses/<sha>.json` — that literal SHA-keyed
ingest is the next step (NOT audio_file population, which is stale advice). Then Essentia →
`track_analysis` (5 now), re-seat the 744 embeddings, then downstream (crates/segments/transitions, all 0).
New thread: brain has **no artist/relationship tables** — the Anna's Archive collab graph has nowhere to live yet.

---

## The one-paragraph picture
Two repos: **slut = identity** (which file is this / where from), the **sole writer of
`music_v4.db`**; **hag = understanding** (MIR, similarity, mixing), **read-only on slut**.
The catalog now lives in **v4** (`track`/`release`/`track_file`, ~31.4k tracks, populated
by a one-shot migration). Live intake is still **v3-native** and redirects to a populated
sibling `music_v3.db` as an interim; the v4 write-side port is **drafted, not built**.

## Where things live
- **DBs:** `slut_db/FRESH_2026/music_v4.db` (write-frozen identity-seam source, `$TAGSLUT_DB`; see `DECISIONS_LOCKED §15`) · sibling
  `music_v3.db` (live intake write target / system-of-record for identity, `$TAGSLUT_V3_DB`) · masters `$MASTER_LIBRARY`.
- **Identity seam (hag's read interface):** `slut:tools/v4/export_identity_seam.py` →
  `identity_seam.jsonl`, keyed `content_sha256` (primary) + `track_id` (secondary),
  ISRC nullable tertiary.
- **Locked decisions:** `decisions/DECISIONS_LOCKED.md`. **Frozen history:** `hag:RELAY.md`.
- **Key specs:** `slut:docs/v4/2026-07-03-ts-stage-membership-and-receipt-spec.md`
  (compilation membership + receipts, v3-lane) · `slut:docs/v4/2026-07-03-v4-intake-write-contract-spec.md`
  (DRAFT — the v4 write-side port) · `slut:docs/reports/v4_storage_layer_port_plan_20260703.md`
  (the v3/v4 redirect diagnosis).

## Open questions between the repos (the only things needing a reply)
- **CLOSED (spine #57, 2026-07-04):** ~~OPEN → slut (spine #54): six orphaned `ref_*`
  tables~~ — **RESOLVED**: tables are slut's own ingest output (`tools/v4/ingest_beatport_reference.py`,
  commit `2496e1de`, 2026-06-30), not a Gemini write. Legitimized via migration 0019
  (`tagslut/storage/migrations/0019_adopt_ref_beatport_layer.sql`, commit `3863e369`).
  Full audit: `slut:docs/reports/ref_beatport_adoption_validation_20260704.md`.
  **Nature gate unblocked on `ref_bp_track` for N4.**
- **OPEN → operator (spine #50, supersedes #49):** ratify the evidence-framed nature
  gate — reject rules, N4 (Beatport-linked >130 BPM), Lexicon-membership-as-weak-signal,
  and go/no-go on the Beatport export calibration test.
- *Recently closed:* **seam transport** — hag consumes the
  published `identity_seam.jsonl`, not a live view (spine #18). **Fingerprint lane** —
  slut's, per `hag:slut_hag_split.md:24`; but 2% coverage so it's a gated no-op in the
  v4 resolver v1 (write-contract §9 Q2).

---

## slut section (identity / acquisition / safety) — maintained by slut
**Done recently:** v4 catalog built (31,445 tracks, gates green); ts-stage v3-redirect
**discriminator bug fixed** (`da06e00a` — empty v4 scaffolding no longer defeats the
redirect); streamrip download-path routing fixed; membership policy locked (§11); Qobuz
metadata-on-download authority fix shipped (`2329e539` + cover-art `10c11f14`, v3 lane);
cover-art xfail closed (`bcc7304a`, suite 54/0); STATE.md current-truth layer + freshness hook.
**Directed (Fable):** v4 intake write-contract §9 — **Q1âQ4 CLOSED**: Q1 coexistence =
incremental-migration bridge on `content_sha256` (not dual-write); Q2 fingerprint = slut-lane
but shipped OFF (2% coverage); Q3 id-map = dissolved (sha256 is the key); Q4 duration-Î =
configurable default. **Q5 OPEN = NEXT PRIORITY: make `music_v4.db` reproducible from the
repo** (no build recipe = catalog-loss risk); resolver+bridge **PARKED — operator decided
2026-07-04 (LEDGER §15, spine #44): v4 stays a read-only catalog, live intake stays v3-native.**
Unparks only when "download → immediately mixable in v4" becomes a real need; Q5 doesn't depend on it.
**Open flag (spine #31):** `_prune_orphan_stage_m3u_files` could trash a populated real
`PLAYLIST_ROOT` on a fresh-db stage run — guard pending intake-owner go-ahead.
**Blockers to the full v4 migration:** (1) no identity match-or-create resolver for v4;
(2) `release_package_membership` migration not applied; (3) live DB build recipe not in
repo (not reproducible); (4) `SCHEMA_v4.sql` under-documents live shape; (5) `@stamps_v4`
sentinel not wired to write commands. Detail: the write-contract spec §5/§9.
**Coverage:** `content_sha256` 97.6% (30,675/31,445), ISRC 84% (26,467), 938 `present=0`.
sha re-baseline via `hash_probe_masters.py` pending (spine #20/#21).

## hag section (understanding / MIR / mixing) — maintained by hag
**Direction (locked):** Essentia on FLAC masters is the analysis path (Offtrack cue
heuristic retired); similarity = pgvector via `tools/similarity/sonic_discovery.py`
(Voyager/Annoy benched, not adopted); rendering = `tools/mixslice/` (Pedalboard removed).
MIR output lives in the taghag DB keyed to the slut seam — **never** in `music_v4.db`.
**Interface with slut:** consumes the published identity seam; `spotify_id` bridge done
(18,492 aliases handed to slut, ingested). **Owes slut:** the seam-transport answer above.
**Automix pool** (`hag:docs/automix/POOL_DEFINITION.md`, awaiting operator sign-off as
proposed §C.13). Membership now **three gates**: nature (mixable material) â§ identity
(present master + `content_sha256`) â§ analysis (5 Essentia moods + `sonic7_v1` embedding).
Eligible now **236** / identity-gate ceiling **30,507** / 938 missing masters. (The 17,707
Lexicon `spotify:` rows are aliases of 17,681 OWNED tracks — round-trip mechanism, not an
excluded population; spine #41.)

**Session 2026-07-04 (spine #40â#54) — what changed:**
- **`sonic7_v1` retrieval defect RESOLVED** (#40): recompute chosen over rename (stored
  `essentia-7d-v1` dim0/dim1 differ from the query vector); **435 `sonic7_v1` rows** upserted,
  matcher candidate query returns candidates again (was 0). `essentia-7d-v1` rows kept.
- **Energy authority = provenance axis** (#41a/#46, LEDGER §A.12): measured energy is hag's,
  **any measurer** (MIK/Lexicon/Essentia); Lexicon **local-file** energy admissible, but
  Lexicon **streaming-row** energy is cached **Spotify** features = provider data (ADR 0007),
  **not** admissible as `sonic7_v1` dim0. `dj_tag.energy` still NULL on all rows (rides 5.0
  default) — closer is a fresh measured pass; ingest side not built.
- **Measured-energy surfaces quantified** (#48): **13,018/30,507** gate members already hold a
  measured energy somewhere. Primary source = **MIK `Collection11.mikdb`** (2.3 GB, 2,101 tracks
  w/ scalar energy + 19,454 trajectory segments) — query the apps' DBs, not exports.
- **MIK energy = trajectory**, scalar is a reduction (#47); live batches on `/Volumes/PLAYGROUND`.
- **`automix_payloads/` linkage** (#52): 27,074 Echo Nest analyses → **17,875 gate members** via
  the ISRC/Spotify bridge; role stays validation-only (#38 pt4 open).
- **Apple MU: sidecars are a dead end** (#53 → #60, corrected 2026-07-04): the **459
  `.cuecifer.json` sidecars yield 0 identity-gated ingest** (present-FLAC â© v4 present-master
  content-hash = 0; â© audio_file = 2 POC leftovers). MU-459 was computed on non-master
  bit-content, disjoint from the gate. Analyzer verified viable (macOS 27, masters reachable
  at `/Volumes/MUSIC/MASTER_LIBRARY/`); real bottleneck is `audio_file`=3,672 vs 30,507 gate.
  Corrected plan: drop sidecar-ingest → probe masters into audio_file (#42) → run analyzer in
  resumable tranches behind operator go. Detail: `hag:docs/automix/MU_COVERAGE_GAP_audit_20260704.md`.
- **Nature gate added** (#49→#50): admission **by evidence** (Beatport presence, MIK/gig history,
  `dj_admission`), **not** by the untrusted genre field; N4 = Beatport-linked >130 BPM rejected
  (mistaken downloads). **Awaiting operator ratification.**
- **ReccoBeats:** no evidence it ever ran (no rows/tables in v3 or v4; only an intake default).
- **v4 `ref_*` layer LEGITIMIZED** (#54 → #57 CLOSED, 2026-07-04): migration 0019 applied;
  nature gate unblocked on `ref_bp_track` for N4 signal.
