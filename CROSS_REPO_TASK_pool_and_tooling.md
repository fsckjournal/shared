# Cross-repo task — pool boundaries → tool-adoption decision

**Status:** OPEN task brief · **Created:** 2026-07-04 by hag · **Owners:** operator + slut + hag
**Terminal deliverable:** a locked decision — *for each analysis feature the automix engine
needs, which tool/source we adopt and in what role* — plus the plan that gets us there.

This is a **prompt for a working session** (Claude and/or Gemini, either repo). It does not
itself decide anything; it routes an agent through the record to a decision the operator ratifies.

---

## 0. How to boot (do this before proposing anything — resolve-from-the-record)

Read, in order, and **cite what you find** (`LEDGER §X`, `spine #N`, `ADR-00NN`, doc:line):

1. `shared/decisions/DECISIONS_LOCKED.md` — the ledger. Especially **§A.12** (analysis-feature
   authorities by **provenance**: measured→hag, provider→slut — the axis that governs this whole
   task), §A.1 (Essentia scoped), §B.5/§B.7 (v4 single-writer, identity SoR), §15 (v4 read-only),
   §C.8–C.10 (matcher/renderer/MIR-home).
2. `shared/STATE.md` — current truth both repos; the "Open questions" header.
3. `shared/handoffs/handoff.jsonl` — the spine. Load-bearing range for this task: **#32→#54**.
4. slut ADRs: `slut:docs/decisions/0007` (ReccoBeats≠Spotify features), `0010` (measured-vs-provider
   boundary — the source §A.12 descends from), `0011` (data-layer invariants).
5. `hag:docs/automix/POOL_DEFINITION.md` — the pool spec (three gates). Its `POOL_SESSION_NOTES.md`
   companion is **superseded for specifics** (see its banner) — trust the spec + spine.
6. Briefs: `shared/knowledge/ANALYSIS_STACK_capability_assessment.md`,
   `REDISCUSSION_essentia_vs_apple_mu.md`.

**Operating rules (binding):** resolve from the record before re-deriving; a locked decision is
not yours to revisit without fresh 3-way agreement; if two sources contradict, **escalate to the
spine** (`shared/bin/handoff-append`), don't silently pick; never hand-append to the spine (use the
tool — it auto-numbers; a hand-numbered id already collided once, spine #51); never write to
`music_v4.db` from hag (§B.5); **verify every inherited number before promoting it** — several
"facts" this session turned out to be ingest gaps, not reality.

---

## 1. Pending issues inventory (tackle all — owner + spine ref + what's needed)

**Decisions awaiting a human:**

| # | Item | Owner | State | Needed |
|---|---|---|---|---|
| **#54** | v4 `ref_*` tables (6 tables, incl. `ref_bp_track` 10,219, `ref_audio_features` 7,931) written into `music_v4.db` by **Gemini** 2026-07-02 — §B.5 single-writer violation, orphaned (no migration/FK/consumer) | **slut** | open | adopt-with-validation vs relocate vs drop; **snapshot v4 first**. hag recommends adopt-with-validation (data is wanted; provider-identity = slut lane). |
| **#50** | Nature gate — evidence-based admission (Beatport presence / MIK-gig history / `dj_admission`), **not** the untrusted genre field; N4 = Beatport-linked >130 BPM rejected | **operator** | open (supersedes #49) | ratify: reject rules, N4 >150-clean vs 130–150-review split, Lexicon-membership-as-weak-signal, go/no-go on the Beatport export calibration test |
| **#38 pt4** | **The matcher feature-space question** — keep `sonic7_v1` on Essentia's 4-mood taxonomy, or migrate to Spotify features (valence/energy/danceability, free at ISRC-scale). Different feature space + coverage/repro trade. | **3-way** | open **by design** | this task's core — see §3 |
| **slut Q5** | Make `music_v4.db` reproducible from the repo (no build recipe = catalog-loss risk) | **slut** | open, NEXT priority | independent of the above; note as a gating risk for anything that reads v4 |

**Implementation gaps (no decision needed — just do, per already-locked direction):**

- **Analyzers ran on three disjoint file sets** (#42/#53): Essentia-analyzed **435**, MIK-batch
  **559**, Apple-MU-sidecar **459** — nearly non-overlapping, and 196 of the Essentia 435 were
  spent on **non-master** files. Fix: point every analyzer at the **identity-gated masters**.
- **Apple MU coverage is an ingest gap, not 3** (#53): **459 `.flac.cuecifer.json` sidecars** on
  disk (167 beside MASTER_LIBRARY masters). Ingest them before re-analyzing.
- **`dj_tag.energy` NULL on all rows** (#46/#48): energy ingest side not built. **13,018/30,507**
  gate members already have a measured energy value in *some* source (primary: MIK
  `Collection11.mikdb` — 2,101 tracks, scalar + 19,454 trajectory segments). Build the ingest.
- **`sonic7_v1` retrieval fixed** (#40, 435 rows) — but only 236 gate members are eligible-now;
  the binding constraint is Essentia mood coverage, not exclusions (#42).
- **Spine hygiene:** the `status` field never auto-closes; #2–5/#20/#32/#45/#49 read "open" but are
  resolved by later events. Worth a one-time reconciliation pass so the open-list is trustworthy.

---

## 2. Pool boundaries — what to discuss and settle

The pool is **three gates** (`POOL_DEFINITION.md`): `nature ∧ identity ∧ analysis`.

- **Identity gate** — settled (present master + `content_sha256`; slut lane). Ceiling **30,507**.
- **Analysis gate** — settled mechanically (5 Essentia moods + `sonic7_v1` row). Eligible-now **236**.
- **Nature gate** — **the live boundary discussion.** Operator's definition: exclude what isn't
  mixable *by nature* (rock, classical, mixed DJ sets, mistaken >130-BPM Beatport grabs). Design is
  **admission-by-evidence, not exclusion-by-metadata** (genre field is untrusted). Open sub-questions
  for the session to resolve with the operator (#50): the reject rule, N4's BPM bands, whether the
  "judgment" genre buckets (Dance/Pop 4.6k, Hip-Hop/R&B, World, Jazz/Funk/Soul) are in/out, and the
  precedence of DJ-history over the BPM heuristic. **Blocked on #54** for the Beatport signal source.

Deliverable of this part: a ratified nature-gate rule set, expressible as the SQL-view sketch in
`POOL_DEFINITION.md §5`, and the resulting **analyzable population** count (≈27.9k with named
excludes; recompute after ratification).

---

## 3. The tool-adoption decision (terminal deliverable)

**Frame it on the §A.12 provenance axis, not tool names** (that axis is locked; re-expressing it as
tool names already caused drift — spine #46). The stack has **redundant coverage** of several
features; the decision is *which instrument we adopt per feature, in what role (owner / enricher /
validation / fallback)*, and the coverage/reproducibility trade each carries.

Produce a filled matrix — one row per feature, columns: **feature · adopted source · role · lane
(§A.12) · coverage today · fallback · open risk**. The candidate sources per feature:

| Feature | Candidate sources (redundancy to resolve) | Governing note |
|---|---|---|
| Identity / provider IDs | slut v4 (`track`/`track_alias`), Beatport `ref_bp_*` (#54) | slut lane (§B.7); #54 must resolve first |
| Provider BPM / initial key | Beatport `ref_bp_track.bpm` (10,185), Lexicon, `canonical_bpm/key` | slut lane, provider (§A.12) |
| Measured BPM / beatgrid | Rekordbox (SQLCipher-locked master.db — export-only), Essentia, Echo-Nest payloads | hag lane, measured |
| Energy scalar (1–10) | MIK `Collection11.mikdb`, Lexicon (local-file rows only), Essentia | hag measured; **Lexicon streaming-row energy is Spotify-cached = provider, inadmissible** (#46/ADR-0007) |
| Energy trajectory | MIK (native — 19,454 segments), Echo-Nest payloads (loudness envelope) | hag measured; feeds cues/`dynamic_evolution` |
| Mood / danceability / genre | Essentia (`track_analysis`), Spotify valence (1 axis ≠ 4-mood) | hag measured; **only Essentia emits the 4-mood taxonomy** (§A.1) |
| Timed structure / loudness / pace | Apple MU (`apple_analyzer`, 459 sidecars), Echo-Nest payloads (27,074 → 17,875 gate members) | hag measured; payloads are **validation-only per #38** unless this decision changes it |
| **Similarity vector (`sonic7_v1`)** | Essentia 4-mood + measured energy/BPM **vs** Spotify-feature space | **#38 pt4 — the pivotal call; everything above cascades from it** |

**The pivotal decision (#38 pt4)** to drive to closure: does the matcher stay on Essentia's 4-mood
`sonic7_v1`, or migrate to Spotify features? Weigh explicitly:
- **Essentia path:** owns the 4-mood taxonomy nothing else emits; local, reproducible, uniform on all
  masters; but requires the mood batch to run (30k tracks) to grow past 236.
- **Spotify-feature path:** free at ISRC-scale via the 17,875-member payload/Anna's-Archive bridge +
  `ref_audio_features` (7,931); but it's **provider** data (slut-lane, ADR-0007 caveats), only 1 mood
  axis (valence), and coverage-bound to the ISRC cohort.
- **Reproducibility constraint:** slut Q5 (v4 not yet reproducible) — any path leaning on v4-resident
  provider tables inherits that risk.

---

## 4. Plan — sequence to the decision

1. **Unblock the inputs.** slut resolves #54 (ref_* disposition) — it gates the Beatport signal for
   both the nature gate and the identity/BPM matrix rows. Snapshot v4 first.
2. **Ratify the boundary.** Operator settles #50 (nature-gate rules). Recompute the analyzable
   population; write the SQL view (`POOL_DEFINITION §5`).
3. **Close the analyzer-coverage gaps** (no decision needed): ingest the 459 MU sidecars; point
   Essentia/MIK/MU at the identity-gated masters; build the energy ingest from `Collection11.mikdb`.
   These make the matrix's "coverage today" columns real instead of ingest-gap artifacts.
4. **Fill the tool matrix** (§3) from the *verified* coverage numbers — every cell cites a query.
5. **Decide #38 pt4** with the matrix in hand: Essentia vs Spotify-feature matcher, with the
   coverage/reproducibility/taxonomy trade explicit. This is the 3-way call.
6. **Lock it.** Record the per-feature adoption as a new `DECISIONS_LOCKED` section (implements §A.12,
   cites it, stays on its axis — do not re-encode as tool names), update `POOL_DEFINITION`, close the
   spine questions, and reconcile the stale `status` fields.

**Deliverables:** (a) filled tool-adoption matrix; (b) ratified nature-gate rule set + population
count; (c) #38-pt4 decision with rationale; (d) the ledger entry + spine closures; (e) an ordered
implementation backlog for the coverage work.
