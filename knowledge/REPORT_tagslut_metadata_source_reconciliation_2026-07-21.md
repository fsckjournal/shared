# Tagslut metadata-source inventory, iceberg, and v4 reconciliation

Date: 2026-07-21

Canonical v4 store: /Users/g/Projects/tag/slut_db/FRESH_2026/music_v4.db
Original Soundiiz union: /Users/g/Downloads/soundiiz/CATALOG_enriched_union.csv

## Executive summary

The conversation began with a Beatport/MP3Tag tagging script and asked whether it could become
an all-purpose Tagslut/TagHag tool. The working boundary became:

- Tagslut: fetched provider metadata, identity, provenance, provider IDs, and source exports.
- TagHag: measured audio analysis, similarity, crates, and mixing intelligence.
- This work: source discovery and read-only reconciliation.

The work produced:

1. A read-only inventory of local exports, provider data, and software backups.
2. A current-v4 reconciler keyed by resolved local path, with ISRC as corroboration.
3. A diagnosis of the ISRC arithmetic problem: old exports and live v4 were different populations.
4. A derived current_v4_union.csv preserving the original Soundiiz union and appending
   current-v4-only preferred paths with current v4 aliases.
5. A separation of the two meanings of iceberg: Soundiiz's excluded listen population and
   the physical /Volumes/ATTIC/ICEBERG storage mount.

No original Soundiiz CSV, v4 database, or audio master was changed.

## 1. Governing source rule

The source inventory says old Picard-era metadata and ISRC values cannot be treated as
unquestionable identity; content evidence must arbitrate. It classifies sources as CONTENT or
TAG and requires corroboration for metadata-derived evidence.

Evidence: knowledge/IDENTITY_DATA_SOURCES_2026-07-17.md:1-9.

The architecture boundary is:

- Tagslut owns identity, provenance, fetched metadata, and v4 writes.
- TagHag owns measured analysis and mixing intelligence.
- Provider exports are evidence, not canonical truth.
- v4 is canonical and slut is its sole writer.

## 2. Source inventory

Command:

    python3 /Users/g/Projects/tag/shared/tools/inventory_source_exports.py \
      --root /Users/g \
      --root /Volumes \
      --out-dir /Users/g/Desktop/tagslut-source-inventory-2026-07-17 \
      --hash-mode small \
      --inspect-sqlite

Verified receipt:

- 847,323 candidate files.
- 0 scan errors.
- Roon backup contents excluded after the operator said not to read Roon backups.
- Sources included Beatport, Tidal, Spotify, Qobuz, MusicBrainz, ListenBrainz, AcoustID,
  Soundiiz, SongShift, TuneMyMusic, Roon, Lexicon, Rekordbox, Mixed In Key, and v4 sidecars.

High-signal files included:

- /Users/g/Projects/tag/slut_db/export_csv/files.csv
- /Users/g/Projects/tag/slut_db/export_csv/track_identity.csv
- /Users/g/Projects/tag/slut_db/export_csv/v_active_identity.csv
- /Users/g/Downloads/soundiiz/CONSOLIDATED_master_v1.csv
- /Users/g/Downloads/soundiiz/CATALOG_enriched_union.csv

Receipt: /Users/g/Desktop/tagslut-source-inventory-2026-07-17/REPORT.md.

## 3. The original population mismatch

| Source | Rows | Distinct normalized ISRCs | Evidence |
|---|---:|---:|---|
| track_identity.csv | 32,196 | 25,090 | March 15 export |
| CONSOLIDATED_master_v1.csv | 31,838 | 25,025 | July 13 export |
| CATALOG_enriched_union.csv | 31,884 | 25,685 | July 13 export |
| Current v4 preferred archive masters | 32,747 | 26,470 | July 21 live DB |

Earlier set arithmetic:

    identity:           25,090
    consolidated:       25,025
    catalog union:      25,685
    identity intersect union: 19,164
    identity-only:       5,926
    union-only:          6,521

Live comparison showed the old track_identity.csv contained thousands of ISRCs absent from
current v4, while the catalog union was v4-anchored. The discrepancy was therefore a
temporal and semantic population mismatch, not bad arithmetic.

## 4. Path-first reconciliation

The v4 path contract is:

    track_file.path is relative to /Volumes/MUSIC/MASTER_LIBRARY

The reconciler resolves both v4 paths and Soundiiz local paths under that root before joining.
It does not use a blind title/artist fuzzy join.

Rules:

1. Exact resolved local path is the primary join.
2. ISRC is corroboration, not an overwrite instruction.
3. ISRC conflicts are surfaced.
4. Provider IDs are reported as evidence, not applied.
5. SQLite is opened read-only with PRAGMA query_only=ON.
6. Audio masters are never moved, renamed, retagged, deleted, or rewritten.

The path trap and its correction are recorded at handoffs/handoff.jsonl:280.

## 5. ICEBERG: two different meanings

### Soundiiz iceberg

Soundiiz's iceberg means the listen membership bloc, not a disk location. Soundiiz's own
Playlist Missing CSV reports its unmatched population; the record says not to reconstruct
that population with fuzzy joins.

Verified record values:

- 2,311 Soundiiz-unmatched tracks excluding the listen/iceberg bloc.
- 435 bare ISRC retry tracks.
- 447 duration-gated ListenBrainz/MusicBrainz recovered ISRCs.
- Approximately 1,400 remained unreachable without the required Roon Path+ISRC export.

Evidence: knowledge/IDENTITY_DATA_SOURCES_2026-07-17.md:42-67 and
handoffs/handoff.jsonl:292.

The 2,311 figure is a Soundiiz-reported unmatched metadata population. It is not a count of
missing masters and not a complete filesystem inventory.

### Physical ICEBERG storage

/Volumes/ATTIC/ICEBERG is a physical storage mount and a separate concept.

The current record says:

- v4 membership values are mix, listen, and unclassified;
- the old work/iceberg value vocabulary was retired;
- listen is the membership equivalent of the former iceberg population;
- many paths that appear absent from MASTER_LIBRARY are physically on ICEBERG.

A later missing-master provenance report classified most of the single-mount missing population
as relocated_to_iceberg, not lost.

Evidence: shared STATE.md:179-187 and handoffs/handoff.jsonl:326.

These must not be conflated:

- Soundiiz iceberg: a service/membership exclusion.
- Physical ICEBERG: a storage location.
- Missing v4 path: a path/presence discrepancy requiring mount-aware provenance.

## 6. Reconciler implementation

Tool:

    slut/tools/v4/reconcile_catalog_union.py

Test:

    slut/tools/v4/test_reconcile_catalog_union.py

Outputs:

- union_reconciliation.csv: one row per original union row.
- provider_enrichment_manifest.csv: provider IDs versus current v4 aliases.
- v4_isrc_gaps.csv: v4 ISRCs absent from the original union.
- current_v4_union.csv: optional derived extension.
- summary.json and REPORT.md.

The extension flag is --extend-union. It preserves original rows and appends v4-only paths
with row_source=v4.track_alias, extension_reason=v4_preferred_path_absent_from_catalog_union,
v4 track/file IDs, provider aliases, and conflict markers.

The extension is a derived review/export file, not an apply file and not a fresh Soundiiz match.

Focused verification: 2 tests passed.

Pushed implementation commits:

- 04378934: initial read-only reconciler.
- 9c9cd578: current-v4 union extension.
- 62172f9: receipt/state update.

## 7. Live reconciliation history

July 17:

- v4 preferred archive masters: 32,040.
- Distinct v4 ISRCs: 25,841.
- Union rows: 31,884.
- Union distinct ISRCs: 25,685.
- ISRC gap: 156.

July 18:

- v4 preferred archive masters: 32,047.
- Distinct v4 ISRCs: 25,848.
- Union distinct ISRCs: 25,685.
- ISRC gap: 163.

The seven new rows were five Nebraska tracks and two Gledd tracks. A follow-up query found
all 163 already had v4 aliases at that point: Tidal 163/163, Beatport 138/163, Spotify 7/163,
308 alias rows, source v3.files.enrich.

July 21:

- v4 preferred archive masters: 32,747.
- Distinct v4 ISRCs: 26,470.
- Original union rows: 31,884.
- Original union distinct ISRCs: 25,685.
- Exact path matches for original union rows: 31,884.
- v4-only preferred paths: 863.
- v4-only paths with ISRC: 788.
- Distinct current-v4 ISRC gaps: 785.
- v4-only paths without ISRC: 75.

The 788 versus 785 difference is three ISRCs represented elsewhere in the original union.

Among the 788 appended ISRC-bearing paths:

- 713 have at least one Beatport, Tidal, or Spotify alias.
- 75 have none of those three provider aliases yet.

Across all aliases on the 863 appended tracks:

- 738 tracks have at least one alias row.
- 2,153 alias rows were present.
- 2,129 alias rows have source v3.files.enrich.
- 24 alias rows have source v3.canonical_isrc.

## 8. Derived union receipt

The extension command was:

    git -C /Users/g/Projects/tag/slut \
      show origin/streaming-enrichment-and-download-triage:tools/v4/reconcile_catalog_union.py |
    /Users/g/Projects/tag/slut/.venv/bin/python - \
      --v4 /Users/g/Projects/tag/slut_db/FRESH_2026/music_v4.db \
      --union /Users/g/Downloads/soundiiz/CATALOG_enriched_union.csv \
      --out-dir /Users/g/Desktop/tagslut-source-inventory-2026-07-17/current-v4-reconcile \
      --library-root /Volumes/MUSIC/MASTER_LIBRARY \
      --check-disk \
      --extend-union

Derived output:

- Original union rows: 31,884.
- Appended v4-only rows: 863.
- Total derived rows: 32,747.
- Duplicate paths: 0.
- Original-row prefix preserved exactly.
- Original Soundiiz CSV unchanged.

Output directory:

    /Users/g/Desktop/tagslut-source-inventory-2026-07-17/current-v4-reconcile/

Key artifacts:

- REPORT.md
- summary.json
- union_reconciliation.csv
- provider_enrichment_manifest.csv
- v4_isrc_gaps.csv
- current_v4_union.csv

## 9. Disk-state correction

Exact path matching and physical disk existence are separate facts.

The July 21 single-mount check against MASTER_LIBRARY found:

- Exact v4 path match for original union rows: 31,884/31,884.
- Resolved files present on MASTER_LIBRARY: 26,097.
- Resolved files absent on MASTER_LIBRARY: 5,787.

This is not a loss verdict. The volume was mounted, but the current record says many MASTER_LIBRARY
missing paths are on physical ICEBERG. A two-mount provenance pass is required before any
negative claim or physical action.

Cross-tab of original union rows:

| Disk state | v4 present flag | Rows |
|---|---:|---:|
| exists | 1 | 25,680 |
| missing | 1 | 4,828 |
| missing | 0 | 917 |
| exists | 0 | 20 |
| missing | NULL | 42 |
| exists | NULL | 397 |

This corrects the earlier conversational overstatement that all union paths existed. The
verified statement is narrower: all union rows matched v4 by resolved path.

## 10. Provider manifest

For the original union population:

- 28,325 eligible_review rows.
- 3,559 review_conflict rows.
- 36,817 provider IDs newly observed relative to current aliases.
- 3,844 provider-conflict provider occurrences.

These are review quantities, not write instructions. No apply mode exists in this tool.

Provider-source rules from the record:

- Soundiiz is a transfer/matching surface, not a library mirror.
- Soundiiz can return service-owned ISRCs different from local ISRCs.
- ListenBrainz to MusicBrainz recovery requires version-aware matching and a file-duration gate.
- AcoustID was a dead end for the tested electronic/no-ISRC population.
- Roon's combined Path+ISRC export remains the missing route for much of the Soundiiz-unmatched population.

## 11. Solved and open

Solved:

- local source/export discovery;
- stale-export diagnosis;
- exact resolved-path reconciliation;
- current-v4-only union extension;
- current provider-alias visibility;
- reproducible read-only receipts;
- explicit separation of Soundiiz iceberg, physical ICEBERG, and missing-path states.

Open:

- mount-aware reconciliation of the 5,787 MASTER_LIBRARY-missing paths;
- provider fetching for the 75 appended ISRC-bearing paths with no Beatport/Tidal/Spotify alias;
- ISRC enrichment for v4-only paths without ISRC;
- any gated provider-ID write to v4;
- the combined Roon Path+ISRC export;
- the Soundiiz listen/iceberg unmatched population;
- all TagHag measured-analysis and mixing-intelligence work, which remains outside this metadata lane.

The correct derived artifact is current_v4_union.csv, not a replacement of the original Soundiiz
export and not a claim that every provider or physical file is solved.

## Evidence index

- Source inventory: /Users/g/Desktop/tagslut-source-inventory-2026-07-17/REPORT.md
- Current-v4 receipt: /Users/g/Desktop/tagslut-source-inventory-2026-07-17/current-v4-reconcile/REPORT.md
- Machine receipt: /Users/g/Desktop/tagslut-source-inventory-2026-07-17/current-v4-reconcile/summary.json
- Identity/source map: knowledge/IDENTITY_DATA_SOURCES_2026-07-17.md
- Current cross-repo state: STATE.md
- Soundiiz/ListenBrainz/AcoustID record: handoffs/handoff.jsonl:292
- Missing-master/ICEBERG provenance: handoffs/handoff.jsonl:326
- Historical union method: handoffs/handoff.jsonl:280
- Reconciler branch: streaming-enrichment-and-download-triage

