# Cross-repo task — pool boundaries → tool-adoption decision

**Status:** OPEN task brief · **Created:** 2026-07-04 by hag · **Owners:** operator + slut + hag
**Terminal deliverable:** a locked, **evidence-based** decision — *for each analysis feature the
automix engine needs, which tool/source we adopt and in what role*, each backed by an attached
experiment result — plus the plan that gets us there. Coverage and lane are tie-breakers, never the
reason a tool is chosen (the standard set when Essentia was adopted on evidence, spine #33).

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

## 3. The tool-adoption decision (terminal deliverable) — **evidence-based**

**The decision is made on evidence of fitness-for-purpose, not on coverage or lane.** This is the
standard the stack already holds itself to: Essentia was adopted and the Offtrack/Echo-Nest cue
heuristic retired **on empirical grounds** — shuffle-control ≈ chance, `Offtrack ∩ Mixonset = 0`
overlap, non-reconstructability (spine #33; `ANALYSIS_STACK_capability_assessment.md §7`). The
assessment is explicit: **"coverage invoked only to break a genuine tie."** So coverage, provenance
lane (§A.12), and reproducibility are **constraints and tie-breakers — never the reason a tool is
adopted.** A tool earns a role by *measurably doing its job*; only then do lane/coverage place it.

**The evidence base is already in hand — this stack's gift is redundancy.** Most features are
measured by *several independent tools*, and there is a real validation corpus. Use both:

- **Cross-source agreement** is evidence. Energy has 3 independent measurers (MIK / Lexicon-local /
  Essentia), BPM has 4 (Rekordbox / Beatport-store / Essentia / Echo-Nest payloads), timed structure
  has 2 (Apple MU / Echo-Nest payloads) — and the payload and MU cohorts **overlap** on the 17,875
  bridged members, a natural head-to-head. Where independent tools agree, trust is earned; where they
  diverge (e.g. half-time BPM), the disagreement itself is the signal and the tie-breaker is which one
  matches ground truth.
- **DJ ground truth** decides the matcher. Real prep/play history exists: MIK collection
  (`Collection11.mikdb`, 2,101 tracks), `gig_set_tracks`/`dj_playlist_track` (populate them),
  `dj_admission` (889 admitted). Tracks the operator actually mixed together are labelled positives.
- **The 27,074 Echo-Nest payloads are the designated validation corpus** (#38) — hold-out truth for
  structure/tempo, and the ISRC bridge to Spotify features for the matcher bake-off.

**Deliverable = a filled matrix, one row per feature, columns: `feature · candidate sources ·
validation test (metric + ground truth) · result · adopted source · role · lane (tie-break only) ·
open risk`.** The **validation-test column is mandatory and comes before "adopted"** — no cell is
filled from coverage alone. Candidate sources and the test to run per feature:

| Feature | Candidate sources | Validation test (evidence that decides) |
|---|---|---|
| Identity / provider IDs | slut v4 (`track`/`track_alias`), Beatport `ref_bp_*` (#54) | agreement of Beatport linkage vs ISRC/alias; #54 must resolve first — lane (slut, §B.7) is the tie-break, not the decider |
| Provider BPM / initial key | Beatport `ref_bp_track.bpm` (10,185), Lexicon, `canonical_bpm/key` | agreement with measured BPM; disagreement rate = the half-time-detector signal |
| Measured BPM / beatgrid | Rekordbox (export-only, SQLCipher), Essentia, Echo-Nest payloads | cross-tool agreement on the overlap cohort; accuracy vs beatgrid on a hand-checked sample |
| Energy scalar (1–10) | MIK `Collection11.mikdb`, Lexicon (local-file only), Essentia | 3-way agreement; correlation with the energy trajectory's own peak; **Lexicon streaming-row energy is provider Spotify cache = inadmissible** (#46/ADR-0007) |
| Energy trajectory | MIK (native, 19,454 segments), Echo-Nest payload loudness envelope | do the two envelopes agree on peak/breakdown placement on the overlap cohort? |
| Mood / danceability / genre | Essentia (`track_analysis`), Spotify valence | Essentia is the **only** 4-mood emitter (§A.1) — test is discriminative validity (do its axes separate tracks a DJ hears as different?), not a bake-off it can't have |
| Timed structure / loudness / pace | Apple MU (`apple_analyzer`, 459 sidecars), Echo-Nest payloads (17,875 members) | head-to-head on the overlap cohort: section-boundary agreement; which better predicts real transition points |
| **Similarity vector (`sonic7_v1`)** | Essentia 4-mood space **vs** Spotify-feature space | **the decisive bake-off — see below** |

**The pivotal experiment (#38 pt4).** Do **not** decide Essentia-vs-Spotify-feature matcher by argument.
Run it: build both candidate vectors on the **same** cohort (the 17,875 members that have Essentia
moods *and* payload/`ref_audio_features` Spotify features), and score each space against DJ ground
truth with a **shuffle-control** (the exact test that settled #33):

- *Positives* = track pairs the operator actually mixed / sequenced (gig history, real sets, MIK-adjacent).
- *Metric* = do true neighbors rank above random pairs (precision@k, or median-rank of positives vs a
  shuffled null)? A space whose positives ≈ chance is rejected, whichever tool it came from.
- *Then* apply constraints as tie-breakers only: coverage (Essentia = uniform on all masters once the
  batch runs; Spotify = ISRC-bound), reproducibility (slut Q5 — provider tables in v4 inherit that
  risk), and provenance (§A.12: Essentia moods are hag-measured; Spotify features are slut-lane provider).

The decision is whatever the shuffle-control says, constrained by — not overridden by — coverage/lane.

---

## 4. Plan — sequence to the decision

1. **Unblock the inputs.** slut resolves #54 (ref_* disposition) — it gates the Beatport signal for
   both the nature gate and the identity/BPM matrix rows. Snapshot v4 first.
2. **Ratify the boundary.** Operator settles #50 (nature-gate rules). Recompute the analyzable
   population; write the SQL view (`POOL_DEFINITION §5`).
3. **Close the analyzer-coverage gaps** (no decision needed): ingest the 459 MU sidecars; point
   Essentia/MIK/MU at the identity-gated masters; build the energy ingest from `Collection11.mikdb`.
   These turn "coverage today" from ingest-gap artifacts into real numbers **and** assemble the
   overlap cohorts the experiments need.
4. **Build the ground truth** (the gate for everything downstream): assemble the labelled positive
   pairs — real DJ sets / gig history / MIK-adjacency / `dj_admission` — into a held-out evaluation
   set. Without this, step 5 cannot run and the decision is opinion, not evidence.
5. **Run the experiments** (§3) — this is where the decision is actually made, not step 6:
   - cross-source agreement per feature (energy ×3, BPM ×4, structure ×2) on the overlap cohorts;
   - the **#38-pt4 shuffle-control bake-off**: Essentia-space vs Spotify-feature-space scored against
     the ground truth, positives-vs-null. Record precision@k / median-rank, not adjectives.
   Every matrix cell's "result" column is a number from this step.
6. **Fill the matrix and let the evidence decide.** Adopt per feature by test result; invoke
   coverage/lane/reproducibility **only** to break a genuine tie (assessment §7). If an experiment is
   inconclusive, say so and keep the tool provisional — do not resolve it by lane.
7. **Lock it.** Record the per-feature adoption as a new `DECISIONS_LOCKED` section (implements §A.12,
   cites it, stays on its axis — do not re-encode as tool names), with the **evidence attached**
   (the query/metric that decided each). Update `POOL_DEFINITION`, close the spine questions, reconcile
   the stale `status` fields.

**Deliverables:** (a) the ground-truth evaluation set (reusable); (b) experiment results per feature +
the #38-pt4 bake-off numbers; (c) filled tool-adoption matrix, every cell backed by a metric; (d)
ratified nature-gate rule set + population count; (e) the ledger entry (evidence attached) + spine
closures; (f) an ordered implementation backlog. **A decision without an attached experiment result is
not done** — that is the bar this task is held to.
