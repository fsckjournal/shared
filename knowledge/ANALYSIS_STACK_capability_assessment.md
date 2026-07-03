# Objective capability assessment — MIK · Rekordbox · Apple Music Understanding · Essentia

**For spine #32. This is a *complementary stack*, not a contest.** All four are either already owned (MIK, Rekordbox, Apple MU on-device) or open-source (Essentia), so cost/licensing is not a deciding axis. The real question is **what each uniquely brings, where they overlap, and who should own each feature** — with coverage invoked only to break a genuine tie.

Capability claims below are from vendor/framework docs (sourced) cross-checked against what your own sessions observed (REM provenance). Where the record is inconclusive, it says so.

---

## 1. What each tool actually produces

**Mixed In Key (MIK 11)** — *owned tool.*
- **Key** (Camelot/standard) — marketed best-in-class, and it's your locked authority.
- **Energy Level 1–10**, per-track **and per-segment** — MIK's signature; nothing else outputs this exact scale.
- Up to **8 cue points**, tempo, ID3 export into your files.
- Coverage: only tracks you run through MIK. Proprietary but yours; output is portable via ID3.

**Rekordbox 7** — *owned tool.*
- **BPM + beatgrid** (Normal/Dynamic/High-Precision, downbeat placement) — the DJ-grade beatgrid; your locked BPM authority.
- **Key**, **Phrase analysis** (structural sections for the timeline), **AI Vocal detection** (vocal positions), hot cues, waveform.
- Coverage: only tracks analyzed in Rekordbox; export via its DB. Proprietary but yours.

**Apple Music Understanding** (WWDC26 framework, on-device) — *owned via the OS, free, private, offline.*
- Analyzes **six dimensions: key, rhythm, structure, pace, instrument activity, loudness.**
- **Rhythm:** beat + bar timestamps, global **BPM** (nil if <2 beats found).
- **Structure:** three timed levels — **sections, segments, phrases** (this is its standout; richer than Rekordbox phrase).
- **Pace:** perceived energy/momentum as *events-per-minute*, independent of tempo (an energy-like signal, distinct from MIK's 1–10).
- **Loudness:** LUFS-grade (integrated/short-term/momentary/peak).
- **Instrument activity** (a vocal/instrument-presence signal).
- Coverage: **any file, on-device, uniform** — including the FLAC masters. In your stack this was built as `apple_analyzer.swift`, described in-session as *"MIK's energy/structure layer on the real FLAC masters"* (REM `4a0e100f#…`).

**Essentia** (open-source C++/Python MIR) — *open-source, fully scriptable.*
- ~**127 descriptors** in one uniform pass: BPM (histogram), key, **danceability**, loudness, band energies/histograms, onset/structural segmentation.
- **TensorFlow models: genre + mood recognition, and MusiCNN/embeddings** (vector representations).
- Coverage: **any file, all 18k masters, reproducibly from code** — no tool pass, no vendor.
- Note from the deep agreement: even Offtrack's "proprietary AI" was Essentia underneath (REM `dc1a9d57#…`); the retired part was Offtrack's *proprietary `mixability` score* (non-reconstructable), **not** Essentia.

## 2. Capability matrix (✓ = provides, ✓✓ = best/authority, — = no)

| Feature | MIK | Rekordbox | Apple MU | Essentia |
|---|---|---|---|---|
| Key | ✓✓ (your authority) | ✓ | ✓ | ✓ |
| BPM / tempo | ✓ | ✓✓ (your authority) | ✓ | ✓ |
| Beatgrid / downbeats | — | ✓✓ (unique, DJ-grade) | ✓ (beats+bars) | ~ |
| Energy | ✓✓ (1–10, your authority) | — | ✓ (pace) | ✓ (danceability/band) |
| Structure: sections/segments/phrases | cue points | ✓ (phrase) | ✓✓ (3 timed levels) | ✓ (segmentation) |
| Loudness (LUFS) | — | — | ✓✓ | ✓ |
| Vocal / instrument activity | — | ✓ (vocal) | ✓ (instrument activity) | ~ (models) |
| Mood / genre (ML) | — | — | — | ✓✓ (unique) |
| **Similarity embeddings (vectors)** | — | — | — | ✓✓ (**unique**) |
| Uniform coverage of all 18k masters | — | — | ✓ | ✓ |
| Reproducible from code (no vendor/tool) | — | — | ~ (Apple API) | ✓✓ |

## 3. The composition (who owns what) — mostly already settled

Your locked authorities already compose cleanly and complementarily:
- **Energy, Key → MIK** (§ feature authorities).
- **BPM, beatgrid → Rekordbox.**
- **Structure/segments, loudness, pace, on-device analysis of the masters → Apple MU** (`apple_analyzer`).
- **What's left, and unique to Essentia → similarity embeddings, mood/genre, danceability, and a uniform reproducible descriptor baseline across every master.**

Read that last line carefully: it's exactly the set the other three **don't** produce.

## 4. So is Essentia obsolete? Split the claim.

- **For scalar DJ features it IS redundant** — energy (MIK), key (MIK), BPM/beatgrid (Rekordbox), timed structure (Apple MU) are all owned better elsewhere. If Essentia were only being used for those, "obsolete" would be right.
- **For its unique contributions it is NOT replaceable by the other three:**
  1. **Similarity embeddings** — vectors for the pgvector matching engine (§C.8 `sonic_discovery.py`). None of MIK/Rekordbox/Apple MU emit embeddings.
  2. **Mood / genre ML.**
  3. **Uniform, reproducible, vendor-free coverage** of all 18k masters.

**The decisive open question (empirical, checkable in code, not a matter of opinion):**
> **What currently feeds the pgvector similarity vectors in `sonic_discovery.py`?**
> - If they're **Essentia (MusiCNN) embeddings**, Essentia is load-bearing for matching — "obsolete" is false; the right move is to *narrow* Essentia to embeddings + mood, not drop it.
> - If matching uses **scalar features or another embedding source**, Essentia may genuinely be droppable.
>
> REM was inconclusive on this (it confirms pgvector ANN matching but not the vector source — `dc1a9d57#…`, plus an old claude.ai session "searched for vector/pgvector/embedding references across the codebase"). **This is the one thing to grep before deciding.**

## 5. Where coverage breaks the tie (your rule)

Only one overlap is contested on coverage: **structure/energy on the masters** — Apple MU vs Essentia both do it uniformly on all 18k. Here Apple MU wins on *quality + on-device + already-in-your-lane* (it's `apple_analyzer`), so **Essentia isn't needed for structure**. Coverage does **not** rescue Essentia for the scalar features (the others own them). Coverage is therefore irrelevant to the decision **except** if the pgvector embeddings turn out to come from Essentia — then coverage (Essentia = all 18k, uniform) reinforces keeping it.

## 6. Recommended framing for the 3-way

Not "keep vs drop Essentia," but: **"Essentia is retained only for what nothing else provides — similarity embeddings + mood/genre — and retired for everything the owned tools do better."** Confirm the pgvector embedding source; if it's Essentia, this is settled as *narrow, don't drop*. Then update `DECISIONS_LOCKED §A.1` (Essentia = embeddings/mood baseline, not the general analysis engine) and **add §** recording the four-way authority split (MIK / Rekordbox / Apple MU / Essentia), and the hag `dj_engine_stack_decision.md`.

## 7. EMPIRICAL FINDING — the crux, resolved by reading the code

I read the matching engine (`hag/tools/similarity/sonic_discovery.py`). The similarity vector (`VECTOR_SCHEMA = "sonic7_v1"`, `sonic_vector_for()`) is **7 dimensions**:

```python
vec = [energy_norm, bpm_norm, danceability, party, happy, aggressive, relaxed]
```

- `energy` (÷10 → MIK's 1–10 scale) and `bpm` (normalized) = **2 dims from MIK + Rekordbox**.
- `danceability, party, happy, aggressive, relaxed` = **5 dims that are the canonical Essentia mood/danceability model outputs** (Essentia/MTG `mood_party`, `mood_happy`, `mood_aggressive`, `mood_relaxed`, `danceability`). **MIK, Rekordbox, and Apple MU produce none of these.** The engine's whole "producer vibe" / "core identity" logic (`peak_time_house`, `moody_deep`, `warm_dancefloor`, …) is built entirely on these Essentia mood axes.

**Conclusion: "Essentia obsolete" is false for matching.** Five of the seven similarity dimensions — the ones that carry *sonic character*, not just tempo/energy — are Essentia's. Drop Essentia and the vector collapses to energy+BPM (2 dims), gutting the matcher. This also **vindicates `DECISIONS_LOCKED §A.1`**: "native Essentia on the FLAC masters" is exactly what populates the mood dimensions the engine consumes.

**Resolution of #32 (recommended):** Essentia is **retained, narrowed to its unique role — mood/danceability classification (+ any embeddings/genre)** — and retired only for the scalars the owned tools do better (energy→MIK, key→MIK, BPM→Rekordbox, timed structure→Apple MU). Not "keep vs drop" — **keep, scoped.**

**One thing to verify before locking it** (honest caveat): I confirmed the matcher *reads* the mood columns and that their names fingerprint Essentia's models, but I did **not** find the current *writer* in the repo (no `.pb` model or `TensorflowPredict` outside the venvs). So confirm whether the mood values are (a) live-regenerated by an Essentia pass, or (b) populated once and persisted in the taghag DB. That determines the **coverage** action: if new/uncovered masters need mood dims, Essentia must run on them — which is precisely the §A.1 plan. Grep to close it: `mood_`, `danceability`, `TensorflowPredict2D`, model loading in the taghag-import analyzer path.

## Sources
- Apple Music Understanding — [Apple Developer: Music Understanding docs](https://developer.apple.com/documentation/MusicUnderstanding); [WWDC26 "Meet the Music Understanding framework"](https://developer.apple.com/videos/play/wwdc2026/253/); [Synthtopia summary](https://www.synthtopia.com/content/2026/06/23/apple-intros-music-understanding-framework-at-wwdc/).
- Mixed In Key — [mixedinkey.com/features](https://mixedinkey.com/features/); [Mixed In Key 11](https://mixedinkey.com/learn-more/).
- Rekordbox — [rekordbox 7 overview](https://rekordbox.com/en/feature/overview/); [Lexicon: beatgrid analysis](https://www.lexicondj.com/blog/understanding-rekordbox-beatgrid-analysis).
- Essentia — [MusicExtractor docs](https://essentia.upf.edu/streaming_extractor_music.html); [Essentia models (mood/genre/embeddings)](https://essentia.upf.edu/models.html).
- Your stack: `DECISIONS_LOCKED §A.1/§C.8/§C.10`; REM masters `dc1a9d57-12f336bd`, `4a0e100f-12f336bd`, `90150ab2` (`rem query`).
