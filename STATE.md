# STATE — current truth, both repos (read this FIRST)

> **Boot: read `shared/OPERATOR.md`** — how to work with Georges (believe his reports, verify, move-dont-menu, never delete masters, collapse-dont-reconcile).

**This is a snapshot of what is true NOW, not history.** The log
(`handoffs/handoff.jsonl`) is chronological events; this file is the reconstructed
current state so a fresh session (or the operator) does not have to walk the log.
Locked policy lives in `decisions/DECISIONS_LOCKED.md`. **Update this file at the end of
a session; use the log only for events the other side must act on.**

Last updated: **2026-07-10** by slut (LIBRARY HYGIENE CENSUS — terminal read-only audit sizing the nuclear canonicalization pass, spine #170 re #168 — see 🟢 block; prior: MASTER audit 2,020 backlog — 🟡 block; RADICAL COLLAPSE membership + Fork1 alias — 🟢 block)

---

## 🟢 2026-07-10 — LIBRARY HYGIENE CENSUS: nuclear-pass execution plan armed (READ-ONLY, spine #170 re #168)
`slut/tools/v4/library_hygiene_audit.py` (mode=ro+immutable, resumable/cached, argparse; 4 proofs pass: conservation 31445=31445, join delta=38, DB-write-blocked, byte-identical re-run). Whole-library census over all 31,445 track_file rows + both mounts (34,318 disk FLACs). Applies NOTHING — emits `slut/output/library_hygiene_*` (gitignored): `per_file.csv`, `canonical_plan.csv` (the executable plan), `collisions.csv`, `recording_clusters.csv`, `byte_dupes.csv`, `tag_disagreements.csv`, `metadata_noise.csv`, `REPORT.md`.
- **THE SPLIT (decision-ready):** RENAME half = **31,445** files (99% artist-first-legacy shape; exact-conform ~0, shape-conform 5) — **BLOCKED on #168**. METADATA-FIX half = **19,695** files **EXECUTABLE TODAY (#168-independent)**: missing fields (isrc 4,978 / year 3,009 / track_no 946 / disc_no 5,978) + tag↔DB disagreements. The nuclear pass can START on metadata without #168.
- **NEW never-measured:** **13,427** files disagree embedded-tag vs DB (14,423 substantive [album 5,363/artist 4,787/title 3,786/isrc 487] vs 5,888 case/punct noise) — DIRECTION-NEUTRAL (DB may be the canonicalized-correct side; per-field win decided in the pass, not here).
- **Collisions:** 291 groups / 599 files → same ADR-0012 target (dominated by case-only folder/title variants that clobber on the case-insensitive volume; 42 missing-track_no). Gate before any blind rename.
- **Dupes/identity:** byte-dupes (identical sha) = 31 grp / 66 files = ONLY zero-risk collapse set. Same-recording clusters 1,272 — CONFIRMED 1,194 (**mostly LEGIT §11 memberships, NOT a dedupe worklist**) / HELD 78 (weak title+artist+dur or disagreeing-ISRC = the #167 fuzzy trap, NOT dedup-ready). Identity infra tables (recording_cluster/identity_duplicate_cohort/identity_evidence/scan_issues/file_quarantine/file_path_history/file_metadata_archive) all **0** → nuclear pass BUILDS identity from scratch (gap, not contradiction). fpcalc pass OFFERED, NOT run (~4min ro) to harden the 78 HELD — operator go/no-go.
- **Physical:** on-disk∉v4 backlog **3,936** (whole-tree superset of #157's MIK-list 2,020); off-disk 1,027 (≈ membership off_disk 1,101).
- **RANKED BLOCKING DECISIONS:** 1) #168 naming form (gates all renames) → 2) collision policy → 3) HELD-cluster fpcalc go/no-go → 4) #157 §11/§17-aware intake. **Nuclear pass = SEPARATE gated session** (COPY of lib + COPY of v4, dry→copy→verify→swap→path-sync, operator GO per batch, masters never rm'd blind); consumes `library_hygiene_canonical_plan.csv`. This census is TERMINAL — no further analysis proposed.

---

## 🟢 2026-07-10 — dupeGuru CSV classified READ-ONLY into 5 buckets vs v4 (spine #165, NO deletes/writes)
`slut/tools/v4/classify_dupeguru.py` (ro, dry-run-only, no --apply). 2702 rows/1235 groups → `slut/output/dupeguru_classified.csv` + `dupeguru_buckets_summary.md` (gitignored). Join = nfc(casefold(rel-tail)); matched 1589/2702, **#118 delta=0** (CSV↔DB byte-identical this scan, join hand-proven). Buckets (precedence playground>§11>cross-membership>unmatched>true-dupe): **intra_master_true_dupe 338g/786r** (ONLY dedupe candidates; keep-highest reco 338 keep/448 stale, NO action), **playground_intake 195g/433r** (139 alt_master/96 missing → intake #157), **cross_membership 2g/4r** (membership call), **differing_release_§11 105g/225r** (album 84/artist 39 case-folded = matches operator's measured figures; NEVER dedupe #155), **unmatched_in_v4 595g/1254r** (= ingestion backlog #157; spot-checked = alt-named twins of in-v4 canonicals, not norm-misses). **HIGHEST-VALUE: 407 groups have ≥2 matched members with DISAGREEING file_hash_sha256 = real content diffs.** 0 FLAC/file mutations, 0 DB writes (ro proven). No delete pass proposed
  - **Drill-down (spine #166/#167, `slut/tools/v4/sha_disagree_worksheet.py`, ro):** those 407 → shapes **quality_ladder 388 / equal_quality 6 / membership_split 13**. **§11(e) LOCKED** (operator-ruled): quality-upgrade REPLACES worse audio + inherits its membership-bearing metadata (never delete-and-forget; applies even inside §11 compilations); fires ONLY on confirmed same-recording. **Identity gate corrects earlier over-optimism:** only **212/407 identity-confirmed** (177 ISRC + 35 dur±2s); **195 AMBIGUOUS/HOLD**, of which **132 have DISAGREEING ISRCs = likely different recordings** (dupeGuru fuzzy-match = the §11/#155 trap made concrete), ~55 duration-mismatch, 8 no-signal. Replace-eligible ladder losers = **204 (not 388) / 296 HELD**. fpcalc measured ~0.1s/file → all 926 concerned files fingerprintable in ~2-3min READ-ONLY (same Chromaprint as existing 643); confirms the 132-different + rescues ~15 borderline, does NOT convert HELD→upgrade. **Fingerprint pass = offered, not yet run** (operator deciding). Output `slut/output/dupeguru_sha_disagree_{worksheet.csv,summary.md}`. — buckets are worksheets; a keep-highest delete pass (bucket 1 only) would be a SEPARATE gated copy→verify→delete step if operator ever asks.

## 🟡 2026-07-10 — MASTER metadata audit: 2,020 present-on-disk masters ABSENT from v4 (ingestion-gap finding; NO write made)
Tool 1 `slut/tools/v4/audit_master_metadata.py` (read-only auditor) ran over the 2,689-path MIK-reprocess MASTER list (`_backups/mik/mik_reprocess_MASTER_only.m3u8`). Report: `slut/output/tool1_master_audit.{csv,md}` (output/ gitignored, local only).
- **Headline:** of 2,689, only **669 are in v4** (666 canonical path + 3 basename); **2,020 are physically present in `/Volumes/MUSIC/MASTER_LIBRARY` but have NO `track`/`track_file` row** — verified `os.path.exists` all 2,020 at MASTER path, **0** at `/Volumes/ATTIC/ICEBERG` (mount confirmed present) → **not** iceberg-drained, **not** stale paths: a true v4 **ingestion backlog**, outside the 31,445. The 669 in-v4 are all ISRC-null (the un-enriched tail).
- **Join bugs fixed in-tool:** path join must **casefold+NFC** (macOS case-insensitive vol; `AtJazz`vs`Atjazz` false-orphaned ~31); provider IDs join via `ref_bp_track`/`ref_spotify_track` on ISRC, `track` has no provider cols (§12 confirmed). ⚠️ `tagslut/storage/v3/backfill_ids.py` writes v3 husk `track_identity` — **NOT** v4-reusable for Tool 2 without rebasing onto `ref_*`.
- **MIK now complete for this list:** via clean rekordbox+MIK scan (`~/Documents/updated.xml`, 2,523 entries) + `.Mixedinkey/Collection11.mikdb` (full lib 33,596/32,410 keyed): **2,682 keyed**, **7** unkeyable continuous-mixes/sets (§16 pool-excluded), 0 unaccounted.
- **Delivered artifacts** (operator ask): `_backups/mik/mik_reprocess_MIK_keyed.m3u8` (2,682 paths) + `_backups/mik/mik_reprocess_MIK_keyed_links/` (2,682 flat symlinks, 0 broken, collisions disambiguated by album). Builder `slut/tools/v4/build_reprocess_manifest.py` (dry-run default, ro on masters+mikdb).
- **OPEN — ingestion of the 2,020 deferred (operator not-sure, deliberately held):** it's a slut-lane project, NOT a snap write. Prereqs from the record: 639 alt-named (`NN-NN. Title - Artist`) need canonicalizing per **ADR 0012 track-number-first**; each needs a `membership` on arrival (§17); the **411 Various-Artists compilations** hit **§11 (compilations=memberships not duplicates)** — naive dedupe would corrupt memberships. No pressure (MIK-keyed artifacts cover the immediate scan need). Decision pending. Spine question filed.

## 🟢 2026-07-10 — RADICAL COLLAPSE: membership FULLY RULED+APPLIED (mix/listen/unclassified) + Fork1 alias LANDED on real v4 (spine #148/#149)
Split re-verified EXACT vs 07-09: MASTER 25649 / ICEBERG 4695 / BOTH 0 / NEITHER 1101 (31445). #116 "5741 missing" = drain+off-disk, NOT corruption. Purple was NOT a ghost-contradiction — **#135**: real tags (#107) consumed by the MUSIC→ATTIC drain, curation now = LOCATION (#133 closed).
- **MEMBERSHIP — ✅ APPLIED to real `music_v4.db`** (`apply_membership_v2.py --apply`; #134 enum + #140 rule). Enum = **`mix` / `listen` / `unclassified`** (work/iceberg RETIRED as VALUES per #134; mix===work, listen===iceberg). 6089 DISAGREE resolved by **PRIMARY artist** (#140: primary∈listening→listen, else→mix — a feature must not drain a mixable track). **FINAL: mix 24529 / listen 4745 / unclassified 2171.** Reasons: mix_master 19560, feature_only_mix_140 4969, listen_location 4695, off_disk 1101, no_primary_140_unresolved **1070** (HELD — no primary link, `has_files_no_artist_link` #130 overlap, resolves free once artist links backfilled), primary_listening_140 50. Snapshots `music_v4.db.bak_pre_membership_20260710_093854` + `..._v2_20260710_094900`. Tools `slut/tools/v4/apply_membership_v2.py` (supersedes v1 vocab), idempotent/guarded.
- **FORK 1 alias — ✅ LANDED on real v4** (`apply_artist_alias.py --apply`, spine #149). `artist_alias(artist_id,alias,source,…)`, **69** folder aliases (#123 opt-a, #125 set; excludes Isolee/Pacific!/Slo). 0 orphans, idempotent. #123 CLOSED.
- **STILL PENDING:** downstream view regen + one-way Supabase mirror of the `mix` set (NOT regenerated — belongs to the going-forward capture / §15↔#113 v4-sole ratification); 1070 no-primary rows (free once artist links land); **Fork 2 key** (#144, hag-lane read-only: 206 mixed-cause, retarget `musical_key`→`key_camelot` + `0`→NULL unfreeze await hag+operator).
- **FORK 1 artist_alias** (`slut/tools/v4/apply_artist_alias.py`): new `artist_alias(artist_id,alias,source)` mirrors `track_alias`; **69** folder-string aliases loaded from `artist_tail_worksheet` (#123 opt-a, #125 set; excludes Isolee/Pacific!/Slo per #125). Option (b) folder-rename OUT.
- **FORK 2 measured-key** (`hag/tools/reconcile_mik_keys.py`, READ-ONLY re-run 2026-07-10 hag Code, spine #144): six-bucket ledger reproduced **206 / 6,126 / 4,011** (14,846 raw = 98.6% notation). **NEW empirical column verdict:** `key_camelot` agrees with live MIK ZKEY **99.1%** (RPC-consumed), `musical_key` only **71.2%** post-norm (read by NO rpc; contaminated by `ingest_rekordbox`/`ingest_xml` Tonality) → `key_camelot` canonical confirmed, `musical_key` = drifted second store. The **206 are MIXED-CAUSE** (89 compilation/continuous-mix + 117 isolated, 28 relative-major/minor mode swaps) — NOT MIK-supersedes (#129 trap). Receipts: `hag/output/mik_206_candidate_drift_clustered.csv`, `hag/output/PROPOSED_ingest_mik_key_retarget.diff`. NOTHING written to brain.
- **FORK 2 RULED + APPLIED** (operator GO 2026-07-10, spine #153→#154, LEDGER §C.17): **Decision 1 = Option A populate-only.** `ingest_mik` retargeted to write `key_camelot` (stop feeding rekordbox-contaminated `musical_key`); `hag/tools/populate_key_camelot_A.py --apply` filled **5,353** join-recovery rows (`key_camelot` non-null 22,968→28,321; `mik_has_brain_missing` 5,439→**0**). **206 mixed-cause rows UNTOUCHED** (verified: drift bucket held at 206; no MIK key_camelot overwritten — #129 trap NOT fired). Idempotent (re-run=0), 0 sentinels. **Decision 2 = closed moot** (0 live `'0'`/`''` sentinels; ingest guard already prevents them). Cue-duplication hazard in full `ingest_mik` (`insert_track_cues` has no on_conflict) sidestepped via key-only executor. Brain writes were in-lane (hag = sole writer of taghag Supabase); `music_v4.db` untouched.

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
