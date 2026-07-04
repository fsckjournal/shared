# STATE — current truth, both repos (read this FIRST)

**This is a snapshot of what is true NOW, not history.** The log
(`handoffs/handoff.jsonl`) is chronological events; this file is the reconstructed
current state so a fresh session (or the operator) does not have to walk the log.
Locked policy lives in `decisions/DECISIONS_LOCKED.md`. **Update this file at the end of
a session; use the log only for events the other side must act on.**

Last updated: **2026-07-04** by hag (hag section + open-questions; slut section as of
2026-07-03). · Convention: slut maintains the slut section, hag the hag section; the
shared header is either.

---

## The one-paragraph picture
Two repos: **slut = identity** (which file is this / where from), the **sole writer of
`music_v4.db`**; **hag = understanding** (MIR, similarity, mixing), **read-only on slut**.
The catalog now lives in **v4** (`track`/`release`/`track_file`, ~31.4k tracks, populated
by a one-shot migration). Live intake is still **v3-native** and redirects to a populated
sibling `music_v3.db` as an interim; the v4 write-side port is **drafted, not built**.

## Where things live
- **DBs:** `slut_db/FRESH_2026/music_v4.db` (canonical, `$TAGSLUT_DB`) · sibling
  `music_v3.db` (intake redirect target, `$TAGSLUT_V3_DB`) · masters `$MASTER_LIBRARY`.
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
**Directed (Fable):** v4 intake write-contract §9 — **Q1–Q4 CLOSED**: Q1 coexistence =
incremental-migration bridge on `content_sha256` (not dual-write); Q2 fingerprint = slut-lane
but shipped OFF (2% coverage); Q3 id-map = dissolved (sha256 is the key); Q4 duration-Δ =
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
proposed §C.13). Membership now **three gates**: nature (mixable material) ∧ identity
(present master + `content_sha256`) ∧ analysis (5 Essentia moods + `sonic7_v1` embedding).
Eligible now **236** / identity-gate ceiling **30,507** / 938 missing masters. (The 17,707
Lexicon `spotify:` rows are aliases of 17,681 OWNED tracks — round-trip mechanism, not an
excluded population; spine #41.)

**Session 2026-07-04 (spine #40–#54) — what changed:**
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
  `.cuecifer.json` sidecars yield 0 identity-gated ingest** (present-FLAC ∩ v4 present-master
  content-hash = 0; ∩ audio_file = 2 POC leftovers). MU-459 was computed on non-master
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
