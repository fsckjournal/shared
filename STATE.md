# STATE — current truth, both repos (read this FIRST)

**This is a snapshot of what is true NOW, not history.** The log
(`handoffs/handoff.jsonl`) is chronological events; this file is the reconstructed
current state so a fresh session (or the operator) does not have to walk the log.
Locked policy lives in `decisions/DECISIONS_LOCKED.md`. **Update this file at the end of
a session; use the log only for events the other side must act on.**

Last updated: **2026-07-03** by slut. · Convention: slut maintains the slut section,
hag the hag section; the shared header is either.

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
- *(none open right now.)* Recently closed: **seam transport** — hag consumes the
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
repo** (no build recipe = catalog-loss risk); resolver+bridge parked until new downloads must
land in v4 (operator undecided; Q5 doesn't depend on it).
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
*(hag: edit this section on your next session to correct/expand.)*
