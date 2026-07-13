# ISRC-first playlist matching report

Date: 2026-07-13

## Executive summary

The three source exports point to a practical workflow for moving or reconciling DJ-library playlists across services: build a clean track list, make `isrc` the primary match key, keep `title`, `artist`, `album`, and mix/version text as fallback disambiguators, then use the transfer services for what they are good at.

The strongest workflow is:

1. Prepare a CSV or JSON track list with one row/object per recording.
2. Include `isrc` wherever available.
3. Use Soundiiz as the careful validation layer, especially when a match needs manual correction or a persistent matching rule.
4. Use TuneMyMusic as the faster execution layer once the source list has already been verified.
5. Treat UPC as release/package context, not as the main key for track-by-track compilation matching.

Important caveat: an ISRC-first workflow reduces wrong-remix and wrong-release matches, but it is not a mathematical guarantee. A destination service can still lack the recording, carry bad metadata, expose a different release ISRC for the same audio, or choose a bad fallback when the ISRC is absent.

## Source material synthesized

The Cubox exports contain three overlapping threads:

- `songshit json - Google Search.md`: generic JSON structures for songs/playlists.
- `songshit json - Google Search1.md`: using JSON metadata to fetch or match provider IDs such as Qobuz or Tidal IDs.
- `songshift ISRC - Google Search.md`: ISRC, SongShift/Soundiiz/TuneMyMusic matching, UPC limits, and Beatport mix-name handling.

I also checked official current pages for the service mechanics:

- Soundiiz CSV import accepts `title,artist,album,isrc` for playlist and track-list CSV import; only `title` is required, but `artist`, `album`, and `isrc` improve matching.
- Soundiiz matching rules can be created for tracks by `Title - Artist`, URL, or ISRC, and for albums by `Title - Artist`, URL, or UPC.
- TuneMyMusic CSV-to-Qobuz import says it reads uploaded files using track title, artist, album, and ISRC, then reports transferred and missing tracks.

## Recommended data shape

For service import/export, CSV is the lowest-friction format. JSON is better as an internal staging or audit format because it preserves richer provenance and can later be converted to CSV.

Minimum CSV for track matching:

```csv
title,artist,album,isrc
"Song Title (Extended Mix)","Artist Name","Compilation Name","GBABC2300001"
```

Recommended CSV for compilation-heavy Beatport matching:

```csv
title,artist,album,isrc,upc,track_number,mix,source_url,provider_track_id
"Song Title (Extended Mix)","Artist Name","Compilation Name","GBABC2300001","123456789012",7,"Extended Mix","https://...",""
```

Recommended JSON staging shape:

```json
{
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Compilation Name",
  "isrc": "GBABC2300001",
  "upc": "123456789012",
  "track_number": 7,
  "mix": "Extended Mix",
  "source": {
    "platform": "beatport",
    "url": "https://..."
  },
  "provider_ids": {
    "beatport": null,
    "spotify": null,
    "qobuz": null,
    "tidal": null
  }
}
```

## ISRC vs UPC

ISRC identifies the recording. For DJ-library and compilation workflows, that is the useful matching unit: the track, mix, radio edit, extended version, remix, remaster, or live version.

UPC identifies the release package. It is useful when importing or validating an album, EP, label sampler, or compilation as a whole, but it is too broad for track-by-track matching. A compilation UPC can narrow the search to a release, but it still needs track title/number and usually ISRC to select the correct member.

Operational rule: use ISRC as the primary key for tracks; use UPC only as release context or album-level validation.

## Beatport mix-name handling

Beatport often models mix/version text as a separate field, while CSV import tools commonly expose only a `title` field. The safest portable export is therefore:

- Keep a separate `mix` column in the internal source file.
- Create an import-facing `title` value that folds the mix into the display title, e.g. `Song Title (Extended Mix)`.
- Keep `isrc` populated so the folded title is fallback context, not the primary identity key.

This avoids the common failure where a destination picks a radio edit or original mix because the import text omitted the mix/version phrase.

## Tool roles

Soundiiz is best treated as the validation and correction workbench:

- CSV import supports `title,artist,album,isrc`.
- Track matching rules can target ISRC.
- Album matching rules can target UPC.
- It is useful for pinning bad or missing automated matches before running larger syncs.

TuneMyMusic is best treated as the fast transfer runner:

- CSV/file upload supports matching from title, artist, album, and ISRC.
- It provides a transferred/missing report after completion.
- It is a good second step after upstream validation, especially when the source list has already been cleaned.

SongShift is useful contextually for mobile playlist transfer, but the report sources do not establish it as the best bulk/audit interface for this workflow.

## Implications for the tag catalog

For the shared tag system, the workflow aligns with existing locked direction:

- ISRC and provider IDs are identity/provenance data, which belongs on the Tagslut side.
- Beatport and Spotify provider IDs should be captured at intake going forward.
- UPC should not drive recording identity or duplicate handling.
- Compilation membership must remain separate from recording identity: the same recording can legitimately appear on a single, album, and compilation without becoming a duplicate.

The practical export target from Tagslut should therefore be an ISRC-first CSV/JSON packet with release/membership context attached, not a UPC-first album packet.

## Concrete next artifact

If this becomes an implementation task, create an export that emits:

- `title_for_import`: title with mix/version folded in.
- `title_raw`: original title.
- `mix`: separate mix/version field when known.
- `artist`
- `album`
- `isrc`
- `upc`
- `track_number`
- `source_platform`
- `source_url`
- known provider IDs: `beatport_id`, `spotify_id`, `qobuz_id`, `tidal_id`
- local identity fields: `track_id`, file hash, path, and membership/release context.

That keeps the import tools happy while preserving enough local evidence to audit any bad match after the fact.

## References

- Source exports:
  - `/Users/g/Downloads/Cubox-Batch ExportArticles-All-4 Bookmarks/songshit json - Google Search.md`
  - `/Users/g/Downloads/Cubox-Batch ExportArticles-All-4 Bookmarks/songshit json - Google Search1.md`
  - `/Users/g/Downloads/Cubox-Batch ExportArticles-All-4 Bookmarks/songshift ISRC - Google Search.md`
- Official Soundiiz CSV format: https://support.soundiiz.com/hc/en-us/articles/360010006793-What-is-the-CSV-format-to-import-playlists-and-favorites
- Official Soundiiz matching rules: https://support.soundiiz.com/hc/en-us/articles/360012449999-Adding-a-matching-rule
- TuneMyMusic CSV-to-Qobuz import: https://www.tunemymusic.com/transfer/csv-to-qobuz
