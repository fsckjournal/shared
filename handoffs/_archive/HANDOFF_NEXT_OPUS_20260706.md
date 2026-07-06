# Handover — taghag/tagslut — for the next Opus

**From:** Gemini (agent run), 2026-07-06. **Operator:** Georges.
**Goal:** Queue refinement for the Apple MU scanner & strictly enforcing Nature-Gate.

---

## 1. What was done
1. **Apple MU Scan Execution**: Managed the queue for `run_mu_scan.py` to churn through the 30k track backlog.
2. **Nature-Gate (#50) Enforcement**: The operator explicitly ordered us to apply the Nature-gate ratification (#50) logic ahead of compute work. I wrote a strict SQL-to-Mock script that enforced:
    - **N-Reject on Structure**: Any track > 20 mins OR **< 1 minute** (added to `POOL_DEFINITION.md` as of today per operator instruction), OR titled "dj mix"/"continuous mix" is bypassed.
    - **N-Reject on Genre**: Excluded `Rock`, `Classical`, `Metal`, `Alternative`, `Indie`, `Country`, `Folk`, `Blues`, `New Age`, `Chanson`, and `Pop` **UNLESS** they possess a positive signal.
    - **Positive Signals Evaluated**: Only **Beatport presence** (`ref_bp_track`). MIK prep/play history is officially considered "false" (the operator dropped the whole library in, so it's not a curated signal) and Lexicon was dropped previously.
3. **Queue State**: The bypass generator mocked out all failed tracks by writing a `{"skipped": true}` JSON file in `/Users/g/Projects/tag/hag/tools/apple_mu_analyses/`, tricking the scanner into skipping them cleanly without modifying the DB.
    - We preserved operator manual blocks (direct overrides for ~88 pop tracks + explicitly named top-40 artists like Alanis Morissette, Ziad Bourji, The Cranberries, tUnE-yArDs, Greta Van Fleet, Niklas Paschburg, Philippe Katerine, and forced unconditional drops on genres 'Country' and 'Blues').
    - Tracks failing Nature-Gate were successfully bypassed.
    - Tracks that *were* blocked but actually have Beatport presence were *un-bypassed* and restored to the queue.
    - Result: the scan queue was pared down to a solid **~11,347 tracks** (after un-bypassing ~1,069 tracks that had valid Beatport signals but were mistakenly blocked by previous broad genre sweeps).

## 2. Operator Decisions
- **MIK History is not a positive signal:** "signal DJ prep/play history is fasle. i dropped the entire library in MIK".
- **Track Length:** Tracks `< 1 minute` are structurally rejected. Added to `POOL_DEFINITION.md`.
- **Nature-Gate is paramount:** Always enforce `genre-excluded AND zero positive signals`.

## 3. Next Steps for Opus
1. **Finish the Scan:** Let `run_mu_scan.py` finish churning through the 11.3k tracks.
2. **Octave Ear-Pass:** Once the MU scan is completed, check the tempo/key results and do an octave ear-pass on the half/double tempo suspects previously identified (they need their BPMs validated manually by the operator).
3. **Proceed to Automix / Analysis:** Once MU data is fully ingested, proceed to the Essentia batch or directly to Automix matching.
