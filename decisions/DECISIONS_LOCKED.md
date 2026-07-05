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
1. **Essentia (analysis direction) — CONFIRMED & SCOPED.** The Offtrack/Echo-Nest cue heuristic stays
   **RETIRED** (shuffle-control ≈ chance; `mixability` proprietary/non-reconstructable). **Native Essentia
   on the FLAC masters is retained as the owner of the mood / danceability / genre layer** — it writes
   `track_analysis` (`happy, aggressive, relaxed, party, danceability, genres_json`, keyed by master
   `sha256`), which supplies **5 of the 7 dimensions** of the `track_embedding` similarity vector
   (`sonic7_v1`). The 2026-07-03 "Essentia obsolete" conclusion is **superseded by code evidence**
   (spine #32→#35): MIK / Rekordbox / Apple MU produce none of the mood dimensions. Essentia is scoped
   *out* of the scalar features other tools own better — see §12.
2. **Offtrack cue timing = discarded noise.** Do not use Offtrack `cue_sec` for transition timing
   anywhere. (hag's own ΔE-alignment test + slut's inspection agree.)
3. **Klio deferred.** Apache Beam is overkill for 18k local FLACs; plain local multiprocessing covers
   it. Revisit only at cloud/cluster scale.
4. **Security.** AWS keys / Lambda URLs recovered from the Offtrack binary → local-only work; never
   authenticate against their backend; keep decoders/keys out of both repos.

12. **Analysis feature authorities — by PROVENANCE (measured vs provider), not by tool.** *(Revised 2026-07-04, operator-approved; governed by slut ADR `docs/decisions/0010-tagslut-taghag-analysis-boundary.md` + `hag:docs/architecture/slut_hag_split.md:176`; resolves spine #32 and #45; supersedes the earlier tool-named form. Assessment: `knowledge/ANALYSIS_STACK_capability_assessment.md`.)*
    - **Ownership is by provenance, not by measuring tool.** Which app emits a number (MIK, Rekordbox, Lexicon, Apple MU, Essentia) is an implementation detail, never the owner.
    - **slut owns PROVIDER-sourced values:** provider BPM and initial/provider key (Beatport/Lexicon-sourced `canonical_bpm`/`canonical_key`).
    - **hag owns MEASURED values:** measured BPM + beatgrid; **energy** — both the scalar 1–10 *and* the per-cue trajectory (any measurer: MIK app, Lexicon, Essentia); timed structure/segments, loudness, pace (Apple MU `apple_analyzer`); mood (happy/aggressive/relaxed/party), danceability, genre, and the similarity vector (Essentia, `track_analysis` → `track_embedding`).
    - Similarity engine `sonic7_v1` = `[energy, bpm, danceability, party, happy, aggressive, relaxed]`, all **measured** (hag's lane): dim0 = measured energy scalar (MIK or Lexicon, ÷10), dim1 = measured BPM, dims 2–6 = Essentia mood/danceability. The analyzers are **complementary, not competing**; none replaces another.

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
11. **Compilations are release memberships, never duplicates.** *(Added 2026-07-03, operator-approved;
    spec: `slut:docs/v4/2026-07-03-ts-stage-membership-and-receipt-spec.md`.)* Recording identity (ISRC)
    and release membership are different facts: the same recording on an album AND a compilation is two
    memberships of one recording, not a duplicate. Binding on intake: (a) ISRC dedupe governs
    **download avoidance only** — it may never delete, skip-and-forget, or dissolve a membership;
    (b) when the library already holds a **bit-identical** file (`file_hash_sha256` match), the
    compilation slot is satisfied by **copy/hardlink**, not re-download and not silent skip; (c) an
    incoming release grouping is **never re-grouped by ISRC** into albums — "directory scope is not
    release identity" cuts both ways; (d) every skipped/copied/virtual membership decision lands in the
    per-run intake receipt AND as a `release_package_membership` row at intake time — the deferred
    `virtual_release_membership_or_physical_duplicate` CSV parking lot is retired. Physical-by-copy is
    the default; virtual membership is an explicit flag, never a silent fallback.
13. **Qobuz download identity & auth.** *(Added 2026-07-04, operator-confirmed.)* The **paid,
    download-eligible** Qobuz account is **`county-cog.6z@icloud.com`** (user_id **`12779111`**).
    The free account `spindly_rhythms2u@icloud.com` (user_id `12024329`) is **download-ineligible**
    (`IneligibleError: Free accounts are not eligible`) and is what the Postman env holds — so bare
    `ts-auth qobuz` (Postman-import path) silently re-auths the *free* account and clobbers a working
    paid token. Binding: (a) re-auth only via **`tools/auth qobuz --user county-cog.6z@icloud.com`**
    (interactive password prompt; fixed in `slut:tagslut/cli/commands/auth.py`, commit `c369789f` —
    the `--email` branch no longer short-circuits to Postman import); (b) the download engine is now
    **`Sei969/qobuz-dl`** at `~/Projects/qobuz-dl` — the former pinned streamrip fork is fully retired; 
    (c) **auth ≠ download**: fetching a token (Postman/browser/API login) is independent of the 
    downloader. `qobuz-dl` must have dynamic app_id overriding disabled in its `qopy.py` to prevent 
    it from invalidating `user_auth_token`s generated by older app_ids.
14. **A complete, integrity-valid Qobuz download is never discarded on a nonzero qobuz-dl exit.**
    *(Revised 2026-07-04, operator-approved.)* `qobuz-dl` can exit nonzero on a benign trailing error 
    (e.g. a single track unavailable at the target hi-res quality) while still writing a complete, valid 
    album to disk. `slut:tools/get` now salvages this: on nonzero exit it runs `validate_qobuz_dl_flacs` 
    against the touched batch root and, if every FLAC passes integrity, logs a warning and continues to 
    intake instead of aborting. Only a **missing or corrupt** batch is a real download failure. The 
    manual recovery for an already-staged album remains `ts-stage '<staged dir>' --source qobuz --execute` 
    (registers → integrity → promote → verify off the on-disk files, no re-download).
15. **v4 is write-frozen but LOAD-BEARING for the identity seam; live intake stays v3-native. The resolver + append-only
    bridge are PARKED; the only near-term v4 work is reproducibility (Q5).** *(Added 2026-07-04,
    operator-decided; amended 2026-07-05).* New download output does **not** need to appear in `music_v4.db` near-term. 
    Intake keeps writing the v3 layer (`track_identity`/`asset_file` → `music_v3.db` via the row-presence redirect). 
    However, **v4 is NOT inert or out of the path**: the taghag brain population strictly reads `v4.track_file.file_hash_sha256` 
    because v3 lacks full SHA coverage. Consequence (accepted): a freshly downloaded track is invisible to
    v4/hag until the next migrate run — acceptable because hag's automix pool is curated and fed by the
    identity gate + ISRC/Essentia batch enrichment (spine #39/#40/#41), not by live v4 intake.
    **The one thing that flips this:** a real need for "download → immediately query-able/mixable in
    v4" — then build `identity_resolver.py` (spec §3) and wire the append-only bridge (make
    `migrate_v3_to_v4.py` append-only, spec §6). **NOW (independent of this, standing risk):** Q5 —
    make `music_v4.db` reproducible from the repo (`v4-intake-write-contract-spec.md` §5.3/§9.5). The
    strategy (incremental-migration bridge, NOT dual-write, NOT a full intake rewrite) remains as
    decided by Fable review 2026-07-03 in that spec §6 whenever the bridge is built.

## C. HAG-LANE decisions (hag's call — recorded by REFERENCE, not re-authored by slut)
See `hag:docs/architecture/dj_engine_stack_decision.md`. In brief, endorsed against existing code:
8. **Matching = existing `tools/similarity/sonic_discovery.py` (pgvector ANN).** Voyager/Annoy **not
   adopted** — `test_voyager.py` stays a bench, revisited only if pgvector is measured to fall short.
9. **Rendering = existing `tools/mixslice/`.** Pedalboard **not adopted** (spike built + removed
   2026-07-02); no second renderer. Transition cue timing comes from mixslice's beatgrid.
10. **MIR / embeddings / cues / Essentia output live in the taghag DB**, keyed to the slut identity
    seam — never in `music_v4.db`.
16. **Automix pool membership (nature gate).** *(Added 2026-07-05).* A track is in the automix pool iff (nature) it is mixable material by *evidence*: not `rejected` in `dj_admission`, not a mixed DJ set/continuous mix, not N4 (Beatport-linked with a 140s *store* BPM as a flag, verdict decided by genre + Essentia mood, not BPM alone), and not genre-excluded-with-zero-positive-DJ-signals — where positive signals are Beatport presence, MIK/gig prep history, and manual `admitted` (which overrides everything; genre is an untrusted corroborator, never a sole excluder; Lexicon library membership is **not** a signal — dropped as circular), **and** (identity) it is an active v4 track whose `archive_master` FLAC is present on disk under MASTER_LIBRARY with a `content_sha256`, **and** (analysis) its latest `track_analysis` carries all five Essentia mood/danceability values and it has a `track_embedding` row in the matcher's vector schema. The nature gate also bounds the analysis batches themselves. ISRC/spotify_id, measured energy, measured BPM/beatgrid, and Apple MU structure are enrichers — they affect mix quality and enrichment reach, never membership. Membership is evaluated per v4 track identity. Spec: `hag:docs/automix/POOL_DEFINITION.md`.

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
