# Cross-repo task — Roon "Mating Tracks in Shuffle" live extension

**Status:** OPEN task brief · **Created:** 2026-07-04 by hag · **Owners:** operator + slut + hag
**Terminal deliverable:** a working, live Roon extension that, on track-change in shuffle/radio,
queues **one** harmonically+sonically compatible track to play next — via Roon's **control plane
only** — gated on a measured metadata-bridge accuracy number. Beatmatching is explicitly out of
scope (stays mixslice's offline lane).

This is a **boot-and-execute prompt** for a working session (either repo, Claude or Gemini). It
sidesteps the settled DSP-no-go road and does not re-decide it. It compresses the Gemini
feasibility study of 2026-07-04 into instruction + guardrails + the risk to kill first.

---

## 0. Boot (resolve-from-the-record — cite `LEDGER §`, `spine #`, `doc:line` before proposing)

Read, in order:

1. `shared/decisions/DECISIONS_LOCKED.md` — **§B.5** (v4 single-writer = slut; hag NEVER writes
   `music_v4.db`), **§B.7** (identity seam is slut's system of record), **§C.8** (matcher =
   `tools/similarity/sonic_discovery.py`), **§C.9** (renderer = `mixslice` — do **not** build a
   competing renderer or real-time DSP).
2. `hag:docs/architecture/roon_extension_architecture.md` + the June transcripts that settled
   **"Roon API = control-plane only, no data-plane / no DSP injection."** That conclusion is
   **LOCKED** — do not re-derive it. This extension is **additive** to mixslice offline rendering,
   not a reversal of it; record it in the spine, no fresh 3-way needed to start.
3. `shared/STATE.md` — current truth; note `sonic7_v1` eligible-now ≈ **236** gate members.

**Operating rules (binding):** hag read-only on slut (§B.5/§B.7); never write `music_v4.db`;
never hand-append the spine — use `shared/bin/handoff-append` (auto-numbers); escalate genuine
contradictions to the spine, don't silently pick; verify inherited numbers before promoting them.

---

## 1. Goal

In Roon **shuffle/radio**, on each Now-Playing change, queue exactly **one** compatible track to
play next through Roon's control plane. Accept a **standard Roon crossfade** — no beatmatching
(that remains `mixslice/grid_mix.py`'s offline job, §C.9). We trade wobble-free beatmatched
transitions for a live "infinite radio" that is **harmonically sensible**.

Aligns with the north star: *the smallest next outcome is one identity-anchored, harmonically
ordered selection that plays in Roon.*

## 2. Architecture

```
Node (RoonApiTransport)  — detect Now-Playing {title, artist}
   -> spawn Python oracle (IPC; JSON over stdout)
   -> oracle returns mate {title, artist}
   -> Node (RoonApiBrowse) — search library, resolve item_key, fire "Play Next"
```

Roon's `node-roon-api` exposes **no** `enqueue(track_id|path)`. All queuing is done by
programmatically driving `RoonApiBrowse` (Library → Search → Tracks → [mate] → Play Next). In
shuffle/radio, an explicit Play Next inserts at the top of the queue, then Roon resumes its
shuffle behavior — which is exactly the desired "cue a mate next" experience.

## 3. Constraints (binding)

- **hag read-only:** the oracle only **queries** the taghag similarity DB to find the mate. No
  writes to `music_v4.db` or anything in slut's lane (§B.5/§B.7).
- **Metadata-only bridge is the weak seam.** Roon exposes no file path, so `{title, artist}` is
  the **only** link back to taghag's `content_sha256`-keyed identity. This is the single point of
  failure and is treated as the primary feasibility risk below — not an afterthought.
- **No mixslice, no DSP:** native Roon playback plays the queued track; the transition is
  whatever the user's gapless/crossfade settings are.

## 4. De-risk FIRST — gate the build on these (before scaffolding `app.js`)

1. **Fuzzy-match accuracy.** Sample N real Roon Now-Playing `{title, artist}` payloads; run them
   through the taghag resolver over the ~31k library; **measure mismatch / no-match rate**. If
   title/artist can't reliably resolve to the correct `content_sha256`, the extension silently
   queues wrong tracks — surface the number before writing any Node.
2. **Mate availability.** `sonic7_v1` eligible-now ≈ 236 (STATE.md). Quantify how often the
   oracle returns a **confident** mate vs. nothing, and define the fallback explicitly (let Roon
   shuffle proceed untouched).

## 5. Deliverables (in order)

1. **`tag/hag/tools/automix/roon_oracle.py`** — lightweight CLI `--artist --title`; fuzzy-resolve
   to internal track id; call the existing `sonic_discovery` engine for the top-1 compatible mate
   (Essentia moods + measured energy + Camelot key); emit result as JSON to stdout. Ships **with**
   the §4 de-risk numbers.
2. **`tag/slut/roon-extension/app.js`** — init `node-roon-api` + `-transport` + `-browse`;
   subscribe to the zone's Now-Playing event; spawn the oracle; implement the `RoonApiBrowse`
   chain (Library → Search → Tracks → [mate] → Play Next) as a **reusable, retry-safe utility**
   (this browse chain is the hardest part of the Roon API).
3. **Spine note + short run/verify doc** recording the extension as additive-to-mixslice.

## 6. Approval gate

Land the §4 de-risk numbers (metadata-bridge accuracy + mate-availability rate) and report them
**first**. Scaffold `app.js` only after the bridge accuracy is shown acceptable. A build that
starts before the bridge is measured is building on the one seam most likely to be unreliable.
