# Energy backfill + automix pool — state as of 2026-07-07T02:43Z

Boot-and-resume doc. Numbers are `[verified: <query>]` against Supabase `taghag`
(`rnscghanqopewyfxqjhp`) at the timestamp above. Reproduce, don't inherit on faith.

Context: Gemini ran the energy write overnight (operator was rate-limited on the Max
plan → fell back to Gemini). Claude audited + normalized it and recorded this. Spine #99.

---

## 1. What changed this session

- **MIK energy is finally in the brain.** `dj_tag.energy` went from effectively
  unpopulated (spine #39/#41: "rides the 5.0 default", the ingest "never ran") to
  **26,285 distinct `audio_file_id`s** populated.
- **Claude normalized the column** (one txn): 331 rows with `energy='0'` (off the MIK
  1–10 scale) → NULL; ~40 float-strings (`'9.0'`) → int-strings (`'9'`). Column is now
  clean 1–10.
- **Listening-artist gate wired.** `is_listening_artist` flag set true for 246 artists
  from `fable_iceberg_prompt.md`; exclusion + remix/extended override added to
  `tools/similarity/sonic_discovery.py`.

## 2. ⚠️ How the energy was written — usable, but NOT §47-compliant

`[verified: opusvsgemini.md L181-214]` Gemini parsed the **first** `Energy N`
`POSITION_MARK` per track from `hag/master.xml` (26,396 tracks) and wrote that **single
scalar** onto `dj_tag` rows where `tag_source='rekordbox_xml'`.

Two deviations from the locked record — a **gap to close, not a contradiction**:

1. **Scalar-first-cue, not the trajectory.** Spine #47 + DECISIONS_LOCKED §12: MIK's
   native output is the per-track energy *trajectory* (8–16 marks); the 1–10 scalar is
   "a derived reduction, not the measurement", and ingest "should store the full mark
   sequence… not discard the trajectory." Only the first mark was kept. The first cue's
   energy is a *proxy* for track energy, not the track rating.
2. **XML-sourced.** Operator: "that xml is garbage." §12 source-of-truth =
   `Collection11.mikdb` `ZENERGY` (33,596 songs), not the Rekordbox XML export.

**Recommended supersede** (open question on spine #99): backfill from
`Collection11.mikdb.ZENERGY` per-track scalar (and optionally store the trajectory in a
cue/observation table), then replace the XML-derived values. Provenance-mark so the
XML-first-cue values remain distinguishable until superseded.

## 3. Verified live numbers

Energy distribution (post-normalize) `[verified]`:

```
1:527  2:3128  3:3079  4:6338  5:4390  6:6459  7:1694  8:392  9:212  10:33
```

Signal coverage + the pool `[verified: query below]`:

| Signal | Count |
|---|---|
| MU sidecar (`apple_derived_features`) | 19,819 |
| MIK key (`dj_tag.key_camelot`) | 24,571 |
| MIK energy (`dj_tag.energy`, distinct afid) | 26,285 |
| RXB BPM (`dj_tag` bpm, `tag_source=rekordbox_xml`) | 25,075 |
| Spotify payload (joinable via `streaminfo_md5`) | 15,974 |
| **All-5 intersection = automix pool** | **8,754** |

**Binding constraint = Spotify.** The `streaminfo_md5` join yields 15,974 even though
23,312 crosswalk rows carry a `spotify_track_id` — the gap is crosswalk rows without a
`v3_streaminfo_md5` (or `audio_file` rows without the backfilled hash). Closing the
`streaminfo_md5` coverage lifts the pool ceiling more than any other single fix.

The **8,754 is a signal-coverage pool**, not yet the §16 nature-gated pool — it still
needs: `is_listening_artist` exclusion (minus remix/extended + admitted overrides),
Avicii/Guetta hard-reject, and genre-exclude Rock/Classical/Metal. Those trim it down.

### Reproduce queries

Pool (fast — CTE joins, avoids the correlated-subquery timeout):

```sql
with mu as (select distinct audio_file_id id from apple_derived_features),
k as (select distinct audio_file_id id from dj_tag where key_camelot is not null),
e as (select distinct audio_file_id id from dj_tag where energy is not null),
b as (select distinct audio_file_id id from dj_tag where bpm is not null and tag_source='rekordbox_xml'),
s as (select distinct af.id from audio_file af
      join crosswalk_v3v4_identity c on c.v3_streaminfo_md5=af.streaminfo_md5
      where c.spotify_track_id is not null)
select (select count(*) from mu join k using(id) join e using(id) join b using(id) join s using(id)) all5;
```

Energy distribution:

```sql
select energy, count(*) from dj_tag where energy is not null group by energy order by energy::int;
```

## 4. Open items (priority order)

1. **Supersede energy** with `Collection11.mikdb ZENERGY` (+ trajectory per §47). Open Q on spine #99.
2. **Verify the 246 `is_listening_artist` flags** — they were set with `ilike.*name*`
   substring matching, which over-flags (a short name that's a substring of another
   artist). Spot-check before trusting the exclusion.
3. **`admitted` override** reads `dj_admission` from `music_v3.db` at
   `slut_db/FRESH_2026/` — that DB is structurally corrupt (memory:
   `music-v3-db-corruption`); admitted-ISRC counts from it are suspect until v3 is repaired.
4. **Lift the Spotify ceiling**: close `streaminfo_md5` coverage on `audio_file` /
   crosswalk to raise the 15,974 joinable count.
5. **Embeddings remain the real gap** (unchanged): `track_embedding` = 744,
   `track_analysis` = 440. Sonic similarity can't run at scale until Essentia populates these.

## 5. Untouched / unchanged (don't re-verify)

Architecture, join spine (`streaminfo_md5`), key authority (MIK Camelot > apple_key
corroborator), artist graph (13,191 / 41,608 / 15,226), v4-inert direction — all per
DECISIONS_LOCKED §12/§15/§16 and spine #85–#97. Not revisited here.
