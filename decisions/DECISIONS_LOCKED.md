# ⛔ DECISIONS — LOCKED (do not revisit without a fresh 3-way agreement)

**As of 2026-07-02.** Agreed by: user + slut-side Opus + hag-side Opus.
**Canonical single source of truth** — this file lives in the shared spine
(`~/Projects/tag/shared/decisions/`, remote `github.com/fsckjournal/shared`).
The old per-repo copies (`hag:DECISIONS_LOCKED.md`) and the hand-mirrored block in
`slut:docs/v4/HANDOFF_TO_HAG_2026-07-01.md` are superseded — they are now pointer
stubs, not content. Edit **only this file**.

> **If you are a fresh Gemini or Opus session: read this file FIRST**, before proposing anything
> about mix cues, similarity/matching, rendering, or writes to `music_v4.db`. Cross-agent messages
> go through the handoff spine (`~/Projects/tag/shared/bin/handoff-append`; `RELAY.md` is frozen).
> Decisions are recorded here by the side that owns the lane (see below) — don't
> re-author another side's calls; reference their doc.

## The lane split (from `hag:docs/architecture/slut_hag_split.md` — the governing invariant)
- **Tagslut (slut) owns identity:** ISRC/UPC, provider IDs, `content_sha256`, fingerprint, file
  location, provenance, safety. System of record for "*which file is this and where did it come from.*"
- **Taghag (hag) owns understanding:** audio analysis / MIR, embeddings, cues, crates, transitions,
  similarity, mixing/rendering. System of record for "*what does it sound like / how does it mix.*"
- **Taghag is read-only on Tagslut. It NEVER writes to Tagslut.** Join on `content_sha256` / ISRC.

---

## A. JOINT decisions (all three agreed)
1. **Essentia pivot (analysis direction).** The Offtrack/Echo-Nest cue heuristic is **RETIRED** —
   shuffle-control showed the extracted cues carry ~0 usable signal (≈ 53% = chance) and `mixability`
   is a proprietary, non-reconstructable score. Native **Essentia on the FLAC masters** is the analysis
   direction going forward. (*Where Essentia runs and where its output lands = hag's lane, §C.*)
2. **Offtrack cue timing = discarded noise.** Do not use Offtrack `cue_sec` for transition timing
   anywhere. (hag's own ΔE-alignment test + slut's inspection agree.)
3. **Klio deferred.** Apache Beam is overkill for 18k local FLACs; plain local multiprocessing covers
   it. Revisit only at cloud/cluster scale.
4. **Security.** AWS keys / Lambda URLs recovered from the Offtrack binary → local-only work; never
   authenticate against their backend; keep decoders/keys out of both repos.

## B. SLUT-LANE decisions (slut's authority — hag must honor)
5. **`music_v4.db` has exactly ONE writer: the slut side.** This is the `slut_hag_split.md` invariant
   ("Taghag never writes to Tagslut") + hag's own `AGENT.md` read-only clause. Any hag/Gemini data
   destined for v4 → hand slut the SQL / a payloads file; slut snapshots + validates + applies (as with
   the 18,492 spotify_id aliases). **No direct writes to `music_v4.db` from hag.**
6. **The 2,236 `offtrack_cues` rows in `source_provenance`** were written directly from the hag side on
   2026-07-01 (violating §5) and are MIR (hag's lane), so they don't belong in the slut DB. Disposition:
   they were **removed** 2026-07-02 (hag acked DROP in RELAY MSG-003; deleted off snapshot
   `music_v4.db.bak_pre_offtrack_review_20260702_052835`, FK-clean). If hag wants them they live in the
   taghag brain DB. **DONE.**
7. **Identity/provenance/join-keys/file-location are slut's system of record.** slut provides the
   identity→file-path seam that hag's analysis consumes.

## C. HAG-LANE decisions (hag's call — recorded by REFERENCE, not re-authored by slut)
See `hag:docs/architecture/dj_engine_stack_decision.md`. In brief, endorsed against existing code:
8. **Matching = existing `tools/similarity/sonic_discovery.py` (pgvector ANN).** Voyager/Annoy **not
   adopted** — `test_voyager.py` stays a bench, revisited only if pgvector is measured to fall short.
9. **Rendering = existing `tools/mixslice/`.** Pedalboard **not adopted** (spike built + removed
   2026-07-02); no second renderer. Transition cue timing comes from mixslice's beatgrid.
10. **MIR / embeddings / cues / Essentia output live in the taghag DB**, keyed to the slut identity
    seam — never in `music_v4.db`.

> **slut FYI (not a veto — hag's lane):** the Offtrack `mixability`/`energy` *vector* (distinct from the
> discarded cue *timing*) only exists for the ~18k covered tracks and can't be reconstructed beyond
> them; worth weighing before it becomes a required similarity input. hag's call.

---

## How this stays in sync (so nobody re-litigates settled calls)
- **One copy.** This file is the only canonical ledger. There is no per-repo mirror to keep aligned.
- **Fresh session start:** the boot-block in each repo's `AGENT.md` already does
  `git -C ~/Projects/tag/shared pull` — that pulls this file too. Read it before proposing lane work.
- When a decision changes, edit **this file** and record it in the spine with a `note` event
  (`handoff-append --kind note --summary "DECISIONS_LOCKED §N changed: …"`), then commit+push shared.
- hag-lane changes (§C) also update `hag:docs/architecture/dj_engine_stack_decision.md` (the authority for §C).
