# Identity & enrichment data sources — inventory (2026-07-17)

**Why this exists:** the 2026-07-17 session repeatedly *re-derived* things already on disk
(`integrity_v1.db` was authoritative and sat next to `music_v4.db` the whole time;
`ref_spotify_track` already held AA durations; the AA parquet was already landed). This is the
map, so the next instance checks before deriving. Governed by operator ruling **spine #285**:
*ISRC/metadata are NOT trustworthy identity for old (Picard-era) acquisitions — content must
arbitrate.* Every source below is tagged **CONTENT** (audio-derived, trustworthy) or **TAG**
(metadata-derived, must be corroborated).

---

## 1. Live databases (`~/Projects/tag/slut_db/FRESH_2026/`)

| db | what | coverage | notes |
|---|---|---|---|
| `music_v4.db` | **canonical** store. `track`, `track_file`, `ref_*` | 31,445 tracks / 30,507 present files | slut is sole writer |
| `integrity_v1.db` | **CONTENT.** decode-based integrity | 30,507 | **AUTHORITATIVE for damage.** ran 2026-07-11 |
| `integrity_backlog_v1.db` | **CONTENT.** same, for the un-ingested backlog | 4,324 | NEW 2026-07-17 (#288) |
| `fingerprints_v1.db` | **CONTENT.** Chromaprint | 30,385 of 30,507 | see §4 |
| `lb_mb_isrc_v2.db` | ListenBrainz→MB recovered ISRCs | 913 attempted → **447 confirmed** | **USE THIS** |
| `lb_mb_isrc_v1.db` | first attempt | — | **SUPERSEDED — 39% wrong** |
| `acoustid_isrc_v1.db` | AcoustID probe results | 60 | records the dead end (§4) |

### `integrity_v1.db` — read this BEFORE any damage/duration claim
Columns: `flac_ok, flac_state, md5, total_samples, sample_rate, streaminfo_dur, v4_dur, dur_delta, flags`.
Verdicts: `ok` 21,290 · `NO_MD5` 9,043 · `CORRUPT` 44 · `TRUNCATED?` 20 · `not_found` 110.
- **⚠️ It walks `track_file WHERE present=1` — THE DB, NOT THE DISK.** Any FLAC without a v4 row is
  invisible to it. That hid 4,324 files until 2026-07-17. **Fix is open (#291).**
- **⚠️ md5 blind spot:** only **21,299** live files carry a STREAMINFO md5; **9,208 do not**
  (`00000000000000000000000000000000`). Any md5-based dedup/uniqueness test is ~30% blind and will
  emit false "unique". Do not build an identity check on md5 alone.

### `ref_spotify_track` (inside `music_v4.db`) — **TAG**
`isrc, spotify_track_id, name, album_id, duration_ms, popularity`. 24,442 rows, 23,050 with duration.
Anna's-Archive-derived; **already landed** — do not re-parse the parquet for durations.
Joins to 23,313 of 25,687 ISRC-bearing present masters. **v4.isrc vs this duration: 87.5% agree ≤5s.**
The 12.5% that disagree **conflate wrong-tags with real damage** and cannot be separated by metadata.

---

## 2. Soundiiz (`~/Downloads/soundiiz/`, plus `~/Downloads/tracksCSV*.csv`) — **TAG**

The transfer/matching surface. **Goal: get the library matched on streaming services.**

- **INPUT:** `TracksForSoundiiz-2026-07-13 (4).csv` — `title;artist;album;isrc` **semicolon-delimited**,
  34,296 rows (20,238 with ISRC). Split into 4 ~10k parts (`_part1..4[_deduped].csv` + `.m3u` siblings
  carrying paths).
- **OUTPUT / matched:** `tracksCSV178419*.csv` — `title,artist,album,isrc,platform,trackId,duration,addedDate,url`.
  Per-service: applemusic 8,803 · qobuz 10,000 · spotify 10,000 · tidal 8,316 ×2 (**the two tidal files
  are identical dupes**). Union ≈ 19,125 distinct tracks. Also `albumsCSV*` (upc, albumId) and
  `artistsCSV*` (nbFans) for musicbrainz/listenbrainz/spotify/apple.
- **★ THE UNMATCHED SET — `My *Playlist Missing*.csv`.** Soundiiz **reports its own unmatched tracks**
  (`Track name, Artist name, Album, Playlist name, Type`). **READ THIS. DO NOT reconstruct the match
  with fuzzy joins** — that error cost most of a session.
  → **2,311 unmatched excluding the iceberg (`listen`) bloc**; ~92% of input matched.

**GOTCHAS**
- Soundiiz matches on **metadata**, then returns **the service's own ISRC** — so a literal
  `master.isrc == export.isrc` join fails on every ISRC-aliased recording. It is NOT a real gap.
- Bare-ISRC import works (operator-tested 21/21). Metadata import does not respect ISRC.
- These exports are **not** a library mirror: 71% of their ISRCs (12,949/18,267) exist nowhere in v4.

**Retry lists (`~/Downloads/`)**
- `soundiiz_MISSING_excl_iceberg_ISRC_barelist_20260716.txt` — **435** (had an ISRC; Soundiiz missed them)
- `lb_v2_CONFIRMED_ISRC_barelist_20260717.txt` — **447** (newly recovered, duration-verified)
- ~1,400 of the 2,311 remain unreachable → need the **Roon Path+ISRC export (never delivered)**

---

## 3. ListenBrainz (`~/Downloads/listenbrainz_Geoooorgie_1784047778/`) — **TAG** (but MB-linked)

Full listen history: `user.json` + `listens/<year>/<month>.jsonl`. **116,069 listens, 2012→2026.**
Per record: `track_metadata.{track_name, artist_name}`, `mbid_mapping.{recording_mbid, release_mbid,
artist_mbids}`, `additional_info.{duration_ms, origin_url (spotify track), spotify_album_id}`.
Distinct: **28,605 recording_mbids · 23,313 spotify ids · 36,511 title+artist keys.**

**This is the working ISRC-recovery route** (AcoustID is not). `recording_mbid` → MusicBrainz
`/ws/2/recording/<mbid>?inc=isrcs&fmt=json` → ISRC. **Yield 68% (714/1,044).** MB rate limit 1 req/s;
requires a real User-Agent.

**★ THE BUG — do not repeat it.** v1's normalizer stripped parentheticals, collapsing
`Fiction` and `Fiction (Maya Jane Coles remix)` into one key → **39% of recovered ISRCs were the wrong
recording** (230/597), failing *bidirectionally* (original↔remix). In a DJ library `(Original Mix)` /
`(X Remix)` / `(Extended)` **IS the identity**.
**v2 fix:** version-aware key **+ gate on MB `length` vs the v4 FILE duration** (±5s) →
**458 confirmed / 447 distinct, median delta 0.68s.**
**The real win was the LENGTH GATE, not the key** — v2 picked a different ISRC than v1 on only 30/614
shared tracks; v1's actual flaw was having no way to verify its own answers.
Coverage limit: only 1,260 of the 2,894 no-ISRC `mix` tracks appear in the history at all.

---

## 4. Chromaprint / AcoustID — **CONTENT**

`fingerprints_v1.db` → `acoustic_fp(track_file_id, track_id, file_hash_sha256, rel_path, mount,
duration, fingerprint, fp_error, computed_at)`. **30,385 fingerprinted / 123 errors**, ran 2026-07-13.
Built by `slut/tools/v4/fingerprint_masters.py` — read-only, resumable, sidecar-only, never writes v4.

**★ EXACT INVOCATION — fingerprints only compare if generated identically:**
```
fpcalc -length 120 -json <path>
```

**AcoustID = DEAD END for this catalog — DO NOT RETRY (#287).**
- **0/60 ISRCs.** 63% of audio recognised at ≥0.99 score but with **ZERO MusicBrainz recording links**
  → no MBID → no ISRC. ISRCs live in MB, and this electronic/underground tail is not in MB's graph.
- **KEY TYPES:** repo keys `RTtjLWyPHA`, `2rf3oP7XMV`, `RHlJhHRKyt` are **USER/account keys and are
  REJECTED** (`{"error":{"code":4,"message":"invalid API key"}}`). Lookup needs an **APPLICATION** key
  as `client=` (register at acoustid.org/new-application). Working: `LeDpBBUZfO`. Docs' test key
  `SRaB19v0YAA` works and is the way to prove a request is well-formed vs a key problem.
- **STRUCTURAL LIMIT:** truncated/short files **cannot be fingerprint-identified at all** — a 4s
  fingerprint is not a prefix-match against a 346s recording. Audio identity fails on exactly the
  short-file population you most want to adjudicate.
- **Exact fingerprint equality ≠ "same recording".** It proves *identical decoded audio*. A different
  rip/pregap/offset of a track you own yields a different fingerprint. Good for a SAFE-list; it cannot
  prove absence.

---

## 5. Roon

- **Roon's DB is NOT queryable.** `~/Library/RoonServer/Database/Core/<hex>/broker_4.db/` is a
  **LevelDB** directory (`*.ldb`, `CURRENT`, `MANIFEST-*`, `LOG`) holding proprietary serialized
  objects. The streaming caches (`Cache/{qobuz,tidal,kkbox}_*.db`) are SQLite but are locked and hold
  catalog data, not the local path↔ISRC map. **The Export feature IS the interface.**
- **Exports are split and neither half is sufficient:**
  - `~/Desktop/ROONIDed.csv` — `title;artist;album;isrc` **semicolon**, 21,649 rows, 19,890 with ISRC.
    **No path.**
  - `~/Desktop/ROONIDed.xlsx` — `Album Artist, Album, Disc#, Track#, Title, Track Artist(s),
    Composer(s), External Id (mb:…), Source, Is Dup?, Is Hidden?, Tags, Path`. **Has Path, no ISRC.**
    Paths are RoonMount-form (`/Users/georgeskhawam/Library/RoonMounts/RoonStorage_<hex>/…`) → strip to
    the tail to cross to v4 (**88% tail-match**, per the spine #63 path-crosswalk approach).
  - The two files **sort differently — NOT row-aligned.** Joining xlsx↔csv on metadata only reaches 72%.
  - **★ THE ASK: re-export ONCE with BOTH `Path` and `ISRC` columns** → a pure `path → v4 track_file →
    attach Roon ISRC` join, no fuzzy matching. **Never delivered.** It is the only route to the ~1,400
    Soundiiz-unmatched that ListenBrainz cannot reach.
  - Preliminary (metadata-join, ~72%, therefore soft): Roon supplies an ISRC for **~1,627** of the 2,894
    no-ISRC `mix` tracks, and **~2,230** disagree with the stored ISRC (alias/variation candidates).

- **Roon backups (#290):** exactly ONE exists — `/Volumes/ATTIC/RoonBackups`, **156G, 15 snapshots**,
  Jun 4→Jul 16 2026, marker `_roon_backup_root_` = `ROON BACKUP ROOT v2`, GUID
  `cdf42a2c-ad79-8d41-0aaa-fa892e08d22d`, indexes grow monotonically (no truncation).
  **Restore = point Roon at the ROOT, not a snapshot subfolder.** `/Volumes/bad` holds ZERO Roon data.
  **RISK: single copy on the flaky disk11/ATTIC.** Copy to `/Volumes/BACKUP` (disk14, USB, genuinely
  independent) started 2026-07-17.

- **Roon/SMB daily break:** Core runs on the **Air**; the drives live on this Mac (`g.local`,
  192.168.18.160, **Wi-Fi**, **1-hour DHCP lease**), shared via SMB with **guest access ON**. Roon
  mounts it as a network share (`RoonMounts/`), so when the share drops Roon goes blind and re-ticking
  "Shared" re-registers `smbd`. Fixes: **authenticated share (guest OFF)**, point Roon at **`g.local`**
  not the IP, DHCP-reserve, prefer Ethernet. **Not a disk-sleep issue** — the Mac never sleeps
  (`pmset sleep 0/standby 0/hibernatemode 0`), verified.

---

## 6. Anna's Archive / Kaggle dumps (`/Volumes/ATTIC/kaggle-data/`) — **TAG**

`spotify-aa/tracks.parquet` **23.7 GB**, `artists.parquet`, `track_artists.parquet`;
plus `track_audio_features.parquet`, `10-m-beatport-tracks-spotify-audio-features/`.
Reader: `slut/tools/v4/aa_parquet_to_sqlite.py` (**needs duckdb — NOT installed**; pip is PEP-668
blocked). **Already landed into `ref_spotify_track`** — check that first (§1). This dump is how spine
#64 closed the Spotify bridge offline (+5,424 aliases), making the Soundiiz round-trip redundant.

---

## 7. Archived DBs (`/Volumes/BACKUP/SAD/`) — **historical, mostly VESTIGIAL**

`EPOCH_2026-02-08/music.db` · `EPOCH_2026-02-10_RELINK/` · `EPOCH_2026-02-28/{music,music_v2}.db` ·
`tagslut_artifacts_archive/music_v3.bak.{20260304,20260321}.db` · `dedupe_db/` · `main 3.db`.

The v3-era `files` table has a **full duration-verification schema** (`duration_ref_ms`,
`duration_ref_source`, `duration_measured_ms`, `duration_delta_ms`, `duration_status`,
`duration_check_version`) and a **recovery schema** (`recovery_status`, `recovery_method`,
`backup_path`, `new_duration`) — **BUT THEY WERE NEVER RUN**: `duration_status` = 51 `ok` vs 28,783
NULL; `recovery_status` 100% NULL. **Inherit nothing from them.**
It also has `download_source`/`download_date`/`original_path` — but **`download_date` is all-2026**, a
DB-build artifact, exactly like v4's `track.created_at`. **⇒ Acquisition era is NOT recoverable from
any DB on disk; the Picard-era ruling (#285) rests on operator knowledge, not data.**
`integrity_state` there = 1,028 `corrupt` vs today's 46 — **UNEXPLAINED delta, open (#291).**

---

## 8. The dedup/promotion archive (`/Volumes/BACKUP/bad/Files/Root`)

Residue of a **dupeGuru dedup + promotion pass, Dec 2025**. 52G / 2,045 files. Clean — no corruption,
not an interrupted run.
- `_ARCHIVE/_DEDUPED_DISCARDS/discard_20251222T093455Z/` — **48G, 1,168 flacs**, the *losing* copies.
  Flat tree; original `Artist/(Year) Album/` collapsed into leaf names with `__<hash8>` suffixes.
- `_ARCHIVE/{MUSIC, NEW_LIBRARY}/` — **drained shells: 820 files, ZERO audio** (artwork/lyrics only).
- `_PROMOTION_COLLISIONS/DST_EXISTS_DIFFERENT/` — **2.8G, 27 flacs**. A promotion that **declined to
  overwrite** because the destination existed but differed. Live naming convention. **Genuine
  unresolved project state, not leftovers.**

**★ RISK:** `music_v4.db.promotions` is **0 rows** and no `track_file` references these trees — this
state exists **only on disk, unknown to the DB**. A name-based sample found **4 of 20 discards absent
from MASTER_LIBRARY, ICEBERG *and* v4**; a fingerprint sample found 13/20 with no exact audio twin.
**The 48G pile may hold the only copy of some tracks.** Binding: `feedback_never-delete-masters`,
`feedback_keep-track-receipts-dedup-audio-only`.

**Scan tool:** `~/Downloads/scan_discards.py` → `~/Downloads/discard_scan.db`. Read-only, resumable,
fingerprint-based (`fpcalc -length 120 -json`, matching §4). `REDUNDANT` = exact audio twin exists =
trustworthy. `UNIQUE?` = **no bit-identical twin**, NOT proof of absence (different rip/pregap ⇒
different fingerprint; and 1,182 live files have no fingerprint). Treat as safe-list + review-list.
