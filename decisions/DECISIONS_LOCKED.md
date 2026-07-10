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
    - **Measured-KEY authority = MIK, in Camelot notation.** *(Added 2026-07-06, operator-directed; recorded to spine #85, pending 3-way ack.)* The trusted measured key is Mixed In Key's, stored as **Camelot** — chosen precisely because Camelot is MIK-proprietary, so the notation itself is self-identifying as MIK-sourced and is convertible. Source of truth is the **MIK DB** (`Collection11.mikdb` `ZSONG.ZKEY`, clean Camelot A/B), path-joined to `audio_file`. The rekordbox XML/DB key field is **not** trusted (contaminated with reloaded pre-MIK tags — ~40% stale, verified 2026-07-06), and Apple MU `apple_key` is a **corroborator only**, never the authority (~78% agreement with MIK). Realized in the brain as `dj_tag.key_camelot`. This is the *measured* key; it never overwrites slut's *provider* key (`canonical_key`, above) — same measured-vs-provider split as BPM. Companion measured signals in the same DBs: **BPM/beatgrid = Rekordbox** (MIK writes no tempo), **energy trajectory = MIK**.
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
    However — **REVISED 2026-07-06 (operator, spine #96): v4 is now INERT and OUT OF THE RUNTIME PATH** — frozen, not fed, not deleted. The brain no longer reads `music_v4.db` live; it uses the v4 hashes already ingested into `audio_file.checksum_sha256` + `crosswalk_v3v4_identity` (spine #87) to bridge to v3 identity by ISRC / `v3_content_sha256` / `v3_streaminfo_md5` — **not** a re-key of the brain to v3 full-file SHA, which diverges ~91% (`IDENTITY_KEY_AND_MU_INGEST`). Supabase (taghag) is the brain, and **populating it is the active priority.** The original 2026-07-04/05 stance is SUPERSEDED: ~~v4 is NOT inert or out of the path~~: the taghag brain population strictly reads `v4.track_file.file_hash_sha256` 
    because v3 lacks full SHA coverage. Consequence (accepted): a freshly downloaded track is invisible to
    v4/hag until the next migrate run — acceptable because hag's automix pool is curated and fed by the
    identity gate + ISRC/Essentia batch enrichment (spine #39/#40/#41), not by live v4 intake.
    **The one thing that flips this:** a real need for "download → immediately query-able/mixable in
    v4" — then build `identity_resolver.py` (spec §3) and wire the append-only bridge (make
    `migrate_v3_to_v4.py` append-only, spec §6). **NOW (independent of this, standing risk):** Q5 —
    make `music_v4.db` reproducible from the repo (`v4-intake-write-contract-spec.md` §5.3/§9.5). The
    strategy (incremental-migration bridge, NOT dual-write, NOT a full intake rewrite) remains as
    decided by Fable review 2026-07-03 in that spec §6 whenever the bridge is built.

17. **`track.membership` — ONE authoritative INTENT field, enum `mix`/`listen`/`unclassified`.** *(Added 2026-07-10, operator-ruled: spine #134 vocab, #135 purple, #140 resolver; governed by `slut/docs/decisions/RADICAL_COLLAPSE_one_db_one_membership.md` (accepted 2026-07-10); applied to real `music_v4.db` spine #148.)* Membership is defined by **INTENT**, not disk location — disk/mount/rekordbox-visibility are downstream **consequences**. Enum literals are **`mix` / `listen` / `unclassified`** (spine #134 retired the earlier `work`/`iceberg` VALUES: `mix`===former work, `listen`===former iceberg; `iceberg` is a folder/mount name only, never a membership value). **Purple Finder tags (#107) are NOT a live signal** — they were real, then **consumed by the MUSIC→ATTIC/ICEBERG drain** (spine #135); curation now reads as **LOCATION**, so `listen` backfills from ICEBERG-disk residence. The **MASTER-∩-listening disagreement set resolves by PRIMARY artist** (spine #140): the `track_artist` role=primary/lowest-ord artist ∈ the `LISTENING_ARTISTS` set (§16 / `filter_listening_artists.py`) → `listen`; a listening artist appearing only as a feature/secondary credit does **not** drain a mixable track → `mix`; a track with **no** primary link is left `unclassified` (`no_primary_140_unresolved`), never guessed. Backfill tool `slut/tools/v4/apply_membership_v2.py` (idempotent, guarded). Downstream views (mount / Essentia / one-way Supabase mirror of the `mix` set / rekordbox visibility) are GENERATED from this field — **their regeneration + the v4-sole ratification remain OPEN under §15 ↔ spine #113**; this entry records the field spec, not the v4-inert reversal.

18. **Artist display/romanization aliases persist in `artist_alias`, NOT by folder rename.** *(Added 2026-07-10, operator-ruled; resolves the #123/#125 alias-capture fork; applied to real `music_v4.db` spine #149.)* Folder-string↔canonical-name variants (2Pac≡Makaveli, 松浦亜弥≡Aya Matsuura, حميد منصور≡Hameed Mansoor) live in `artist_alias(id, artist_id, alias, source, confidence, first_seen_at)` (mirrors `track_alias` conventions) — **option (a)**, queryable, lowest-risk. **Option (b) folder rename is OUT** (touches MASTER_LIBRARY paths — hazardous). The 69 worksheet pairs (`artist_tail_worksheet.tsv`, `source='folder_worksheet_20260710'`) are loaded; the 3 Isolée/Pacific!/Slo rows are **merges/kept-split false-positives, NOT aliases** (spine #125), excluded. Loader `slut/tools/v4/apply_artist_alias.py`.

## C. HAG-LANE decisions (hag's call — recorded by REFERENCE, not re-authored by slut)
See `hag:docs/architecture/dj_engine_stack_decision.md`. In brief, endorsed against existing code:
8. **Matching = existing `tools/similarity/sonic_discovery.py` (pgvector ANN).** Voyager/Annoy **not
   adopted** — `test_voyager.py` stays a bench, revisited only if pgvector is measured to fall short.
9. **Rendering = existing `tools/mixslice/`.** Pedalboard **not adopted** (spike built + removed
   2026-07-02); no second renderer. Transition cue timing comes from mixslice's beatgrid.
10. **MIR / embeddings / cues / Essentia output live in the taghag DB**, keyed to the slut identity
    seam — never in `music_v4.db`.
16. **Automix pool membership (nature gate).** *(Added 2026-07-05; revised 2026-07-06 — operator-directed, recorded to spine, pending 3-way ack: MIK/gig prep history dropped as a signal, remix/extended affirmed as mixable, genre-exclude set pinned to Rock/Classical/Metal.)* A track is in the automix pool iff (nature) it is mixable material by *evidence*: not `rejected` in `dj_admission`, not a mixed DJ set/continuous mix, not N4 (Beatport-linked with a 140s *store* BPM as a flag, verdict decided by genre + Essentia mood, not BPM alone), and not genre-excluded-with-zero-positive-DJ-signals — where positive signals are Beatport presence, remix/extended versions (operator 2026-07-06: "the remixes and extended versions definitely stay"), and manual `admitted` (which overrides everything; genre is an untrusted corroborator, never a sole excluder — the ratified genre-exclude set is **Rock/Classical/Metal** per spine #50, do **not** expand it, e.g. to Pop/Alt-Indie/Blues, without a fresh decision; MIK/gig prep history is **not** a signal — dropped 2026-07-06 per operator "i dropped the entire library in MIK", the same circular reason as Lexicon; Lexicon library membership is **not** a signal — dropped as circular; artist-level listening exclusions (never-DJ acts) come from the curated `LISTENING_ARTISTS` roster in `Reference/tagslut-readonly/legacy/handover/iceberg-prompts-2026-06-10/fable_iceberg_prompt.md`, overridden by remix/extended or `admitted` — **not** by DJ-playlist/Rekordbox membership *(operator 2026-07-06, repeatedly rejected: Rekordbox is unreliable — 59.2% unmatched, **0** rows point at MASTER_LIBRARY per POOL_DEFINITION §6 / POOL_SESSION_NOTES, and the override was never computed into the gate, spine #70 caveat)* and **not** by Beatport catalog presence *(operator 2026-07-06: Beatport does not rescue a listening act — supersedes the HANDOFF_2026-07-05/06 "Beatport/playlist presence wins, ~320 protected" framing; those ~320 go to the iceberg)*; **Avicii and David Guetta** (any credit/title/mix including those names) are a **hard operator reject** — no override — flagged for library removal 2026-07-06), **and** (identity) it is an active v4 track whose `archive_master` FLAC is present on disk under MASTER_LIBRARY with a `content_sha256`, **and** (analysis) its latest `track_analysis` carries all five Essentia mood/danceability values and it has a `track_embedding` row in the matcher's vector schema. The nature gate also bounds the analysis batches themselves. ISRC/spotify_id, measured energy, measured BPM/beatgrid, and Apple MU structure are enrichers — they affect mix quality and enrichment reach, never membership. Membership is evaluated per v4 track identity. Spec: `hag:docs/automix/POOL_DEFINITION.md`.

17. **MIK ingest writes `key_camelot`, not `musical_key` (populate-only).** *(Added 2026-07-10, operator GO; implements §12 measured-KEY authority — key_camelot canonical — does not re-author it; spine #144/#153/#154.)* `ingest_mik` now writes the canonical, RPC-consumed `dj_tag.key_camelot` and no longer feeds `musical_key` (a drifted second store also written by `ingest_rekordbox`/`ingest_xml` from ~40%-stale rekordbox Tonality, read by no `find_harmonic_pool` RPC). Verified this session: `key_camelot` agrees with live MIK ZKEY **99.1%** vs `musical_key` **71.2%**. The applied pass was **Option A populate-only** (`hag:tools/populate_key_camelot_A.py`, operator GO): filled **5,353** join-recovery rows (`mik_has_brain_missing` 5,439→0), **without overwriting** any existing `key_camelot` — the **206 mixed-cause** candidate-drift rows (89 compilation/continuous-mix + 117 isolated, 28 relative-key mode swaps) are **untouched** (a blanket MIK-overwrite = the #129 trap, **not** approved). `'0'`→NULL backfill = **closed, moot** (0 live sentinels; ingest guard `_mik_key()` already prevents them). Authority: `hag:docs/architecture/dj_engine_stack_decision.md`.

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
