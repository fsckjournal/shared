# Re-discussion brief — Essentia vs. the Apple-MU / MIK-Rekordbox picture

**For the fresh 3-way (operator + slut advisor + hag advisor). Grounds spine #32.**
Every claim below is cited to REM provenance (`master#turn`) or `DECISIONS_LOCKED §N`. Argue from the record, not memory.

---

## 0. The question on the table

`DECISIONS_LOCKED §A.1` locks **native Essentia on the 18k FLAC masters** as the analysis direction. A later slut/hag session (2026-07-03) declared **"Essentia obsolete."** The ledger was never updated, and Essentia-pivot work is *still in flight* (spine handoff: "pending essentia+numpy dep lines… left UNSTAGED"). Resolve it deliberately — **not by recency**.

## 1. Correction first (so we don't re-discuss a strawman)

The escalation (#33) framed this as "Apple Music Understanding (a black box) replaces open Essentia." The record is more precise. From the 2026-07-03 session (`dc1a9d57#…`, the 12f336bd session), verbatim:

> "FEATURE AUTHORITIES. Locked: **ENERGY←MIK, KEY←MIK, BPM←Rekordbox**; **Apple Music Understanding = complementary** (segment in/out points + BPM/key cross-check via `bpm_agreement_score`), **never owner**. **Essentia obsolete** (apple-analyzer covers MIR natively + gives segment points)."

So Essentia wasn't displaced by Apple MU alone. It was declared redundant because **energy/key/BPM ownership moved to your own DJ tags (MIK, Rekordbox)**, with apple-analyzer covering **segment points** — leaving (the argument goes) nothing for Essentia to own. Apple MU is explicitly *complementary, never owner*. That reframes the whole decision.

## 2. What the deep agreement decided — and why it must not be discarded lightly

This was the deepest, advisor-driven, **evidence-based** discussion. Its conclusions (ledger §A.1–2, §C.10) rest on findings that are still true:

- **The retired heuristics carried no signal.** *"The Offtrack/Mixonset cues carry zero Echo Nest energy-gradient signal — a shuffle-control alignment test beat random only **53% of the time (≈ chance)**."* (`90150ab2#…`)
- **The proprietary score can't be rebuilt and re-chains you to a black box.** *"Mixability is the proprietary Offtrack/Mixonset per-cue score. We only have it for the ~18k covered subset, it **can't be reconstructed** for the rest… building the index on it **re-chains us to the black box we just cut loose**."* (`90150ab2#…`; echoed in ledger §C FYI.)
- **Even the "proprietary AI" was open-source Essentia underneath.** *"Offtrack's 'proprietary AI' is actually heavily reliant on **Essentia — the open-source C++ gold standard for MIR** (BeatTrackerDegara, PitchContourSegmentation), alongside basic TFLite."* (`dc1a9d57#…`, from Gemini)

**The principle that follows:** analysis should be **open, native, reproducible, and uniform across all 18k FLAC masters** — self-controlled, not dependent on a vendor's black box or a per-track tool pass. That principle, not Essentia the library specifically, is what's actually at stake.

**Ledger status quo:** §A.1 (Essentia = direction), §A.2 (Offtrack cue timing = discarded noise), §C.10 (MIR/embeddings/cues/**Essentia output** live in the taghag DB). Apple MU appears nowhere in the ledger.

## 3. The real tensions to resolve

**T1 — Coverage.** Essentia runs uniformly on every one of the 18k masters. MIK and Rekordbox tags exist **only where you've processed a track in those tools**. The *same* 2026-07-03 session measured that coverage as poor: *"rekordbox_track_map is **59% unmatched**, only **3,886 matched** identities, and **ALL location_urls point at the OLD libs** (/Volumes/STILL, MP3_LIBRARY) — **NONE at the FLAC MASTER_LIBRARY**."* (`dc1a9d57#…`). So the authority model may not actually cover the masters today. Does "Essentia obsolete" assume a coverage that doesn't exist yet?

**T2 — Open / reproducible principle (the founding reason).** Essentia is open-source and reproducible from the masters. MIK, Rekordbox, and apple-analyzer are all **proprietary / tool- or vendor-dependent** (apple-analyzer = Apple's on-device black box). Dropping Essentia for them trades away the exact property §A.1 was built to secure. Is that trade acceptable — and was it ever weighed? (It wasn't; Apple MU wasn't in the original frame.)

**T3 — Complementary vs. either/or.** The "obsolete" claim may overstate. apple-analyzer gives **segment in/out points**; Essentia gives **reproducible acoustic features across the full corpus**. Those may be **complementary**, not competing — segments from Apple, baseline features from Essentia, MIK/Rekordbox authoritative where present.

**T4 — What does the automix actually consume?** Per §C.8–9 the engine is pgvector similarity (`sonic_discovery.py`) + `mixslice` rendering (beatgrid timing). If the required inputs are fully served by MIK/Rekordbox (energy/key/BPM) + apple-analyzer (segments) **and** coverage is complete, Essentia is genuinely redundant. If not, it isn't. This is the empirical crux — answerable, not a matter of taste.

## 4. Decision options (frame, don't pre-judge)

- **A — Keep Essentia as the reproducible baseline.** Uniform Essentia MIR over all 18k masters; MIK/Rekordbox authoritative where present; apple-analyzer for segments. Honors the principle + max coverage; cost = running/maintaining Essentia.
- **B — Drop Essentia (adopt the 2026-07-03 position).** Rely on MIK/Rekordbox (energy/key/BPM) + apple-analyzer (segments). Simplest; but proprietary-dependent and exposed to the T1 coverage gap.
- **C — Coverage-gated hybrid.** MIK/Rekordbox where present; **Essentia as the fallback** for the uncovered remainder (which, per T1, is most of the corpus today). Preserves reproducibility exactly where the authority model is thin.

## 5. What the outcome must do

1. Update **`DECISIONS_LOCKED §A.1` and §C.10** to the resolved position (and note where apple-analyzer/Apple MU sits).
2. Update the hag-lane authority doc **`hag:docs/architecture/dj_engine_stack_decision.md`** (governs §C).
3. Close spine **#32** with a `note` recording the change (`handoff-append --kind note --re 32`), then commit+push shared — so this can't silently drift again.

## 6. Provenance (open the masters to verify any quote)

- Deep agreement / evidence: `masters/claude-code/90150ab2-…jsonl`, `masters/claude-code/dc1a9d57-12f336bd…jsonl`, `masters/workbench/4a0e100f-12f336bd…jsonl` (same 12f336bd session, two surfaces).
- Apple-MU / feature-authority position: `masters/claude-code/dc1a9d57-12f336bd…jsonl`.
- Ledger: `~/Projects/tag/shared/decisions/DECISIONS_LOCKED.md` §A.1, §A.2, §C.10 + the §C FYI on the ~18k-only vector.
- Query any of it live: `rem query "<topic>" --limit 8`.
