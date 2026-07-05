# Gemini handover — Supabase brain ingest + Spotify-AA collab graph
**From:** Claude Sonnet, hag session 9c6784d5 — 2026-07-05

> **This is the only current version. If you are reading a document with sections labeled
> §D/§E/§E.1/§E.3, or anything mentioning a filename/naming-template step — that is a
> superseded draft that never existed in this repo (not on disk, not in git history; verified
> 2026-07-05). Discard it. This file uses Phase 0-5 (Section A) and Step 1-3 (Section B) only.
> `git pull` and re-read this file fresh before continuing.**

Boot: `cd ~/Projects/tag/shared && git pull && cat decisions/DECISIONS_LOCKED.md && tail -10 handoffs/handoff.jsonl | python3 -c "import sys,json;[print(json.loads(l)['id'],json.loads(l)['summary'][:100]) for l in sys.stdin]"`

---

## A. Supabase brain — populate from existing data

**Config:** `hag/.env` — `TAGHAG_SUPABASE_URL`, `TAGHAG_SUPABASE_SECRET_KEY`, `TAGHAG_OWNER_USER_ID=d4c61173-8432-432f-b238-9bd72c7285e3`, `TAGHAG_DB_POSTGRES_URL` (direct Postgres).

⚠️ Rotate the service-role key at Supabase dashboard before any INSERT. It was leaked in a prior commit. New key → `hag/.env` as `TAGHAG_SUPABASE_SECRET_KEY`. Verify `TAGHAG_OWNER_USER_ID` exists in `auth.users`.

⚠️ **`TAGHAG_DB_POSTGRES_URL` is currently MISSING from `hag/.env`** (verified 2026-07-05 — only `TAGHAG_SUPABASE_URL`, `TAGHAG_SUPABASE_SECRET_KEY`, `TAGHAG_OWNER_USER_ID`, `VITE_*` are set). Phases 0/2/3/4 below use `psycopg2` and need this. Get it from the Supabase dashboard → Project Settings → Database → Connection string (use the session pooler, port 6543) — this needs the DB password, a separate secret from the service-role key. Add it to `hag/.env` as `TAGHAG_DB_POSTGRES_URL` before running any psycopg2 script. (If you'd rather not add a new secret, Phases 0/2/3/4 can be rewritten to use `TaghagDbClient` REST upserts instead, like Phase 1 already does — slower for ~30k rows but needs no new credential.)

**Two connection modes in the codebase:**
- `TaghagDbClient` (in `hag/tools/taghag_import/db_client.py`) — PostgREST REST API, uses `TAGHAG_SUPABASE_SECRET_KEY`
- psycopg2 direct — used by `extract_dj_slice.py`, needs `TAGHAG_DB_POSTGRES_URL`

---

### Phase 0 — audio_file seam (prerequisite, ~3–5 min)

**What exists:** `hag/tools/taghag_import/extract_dj_slice.py` — reads v3 `files` view → upserts `audio_file` + `dj_tag` via psycopg2. **Not usable as-is** because v3 `files.sha256` is NULL for 23k/34k tracks; the script falls back to `file_key = "streaminfo:{streaminfo_md5}"` for those. The MU sidecar ingest (Phase 1) needs `file_key = "sha256:{sha256}"` to connect, and `apple_music_adapter.py` looks up by exactly that key. If Phase 0 uses streaminfo keys, Phase 1 can't find the rows.

**Write `hag/tools/populate_audio_file.py`** — reads v4 for SHA256 (full 30,507 coverage), enriches from v3 where available, uses psycopg2:

```python
#!/usr/bin/env python3
"""Populate Supabase audio_file from v4 track_file (SHA256 source) + v3 files (metadata)."""
import sqlite3, os, sys
from datetime import datetime, timezone
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

V4_DB = os.path.expanduser("~/Projects/tag/slut_db/FRESH_2026/music_v4.db")
V3_DB = os.path.expanduser("~/Projects/tag/slut_db/FRESH_2026/music_v3.db")
OWNER = os.environ["TAGHAG_OWNER_USER_ID"]
PG_URL = os.environ.get("TAGHAG_DB_POSTGRES_URL") or os.environ["DB_POSTGRES_URL"]
BATCH = 500

# 1. Read v4: sha256 + path for all 30,507 present masters
v4 = sqlite3.connect(f"file:{V4_DB}?mode=ro", uri=True)
v4_rows = v4.execute(
    "SELECT file_hash_sha256, path FROM track_file WHERE present=1 AND file_hash_sha256 IS NOT NULL"
).fetchall()
v4.close()

# 2. Read v3: enrich with metadata where path matches
v3 = sqlite3.connect(f"file:{V3_DB}?mode=ro", uri=True)
v3.row_factory = sqlite3.Row
v3_by_path = {}
for row in v3.execute(
    "SELECT path, size, duration, bitrate, canonical_bpm, canonical_key, "
    "canonical_genre, canonical_sub_genre, canonical_artist, canonical_title, "
    "canonical_album, canonical_isrc, canonical_label, canonical_catalog_number, "
    "canonical_year, canonical_release_date, energy, dj_set_role, "
    "last_scanned_at FROM files WHERE lower(path) LIKE '%.flac'"
):
    v3_by_path[str(row["path"])] = dict(row)
v3.close()

# 3. Upsert into Supabase audio_file + dj_tag
pg = psycopg2.connect(PG_URL)
now = datetime.now(timezone.utc)

audio_rows, tag_rows = [], []
for sha256, path in v4_rows:
    file_key = f"sha256:{sha256}"
    v3r = v3_by_path.get(path, {})
    audio_rows.append((
        OWNER, file_key, path, Path(path).name,
        v3r.get("size"),          # size_bytes
        v3r.get("duration"),      # duration_s
        int(v3r["bitrate"]/1000) if v3r.get("bitrate") else None,  # bitrate_kbps
        "flac",                   # codec
        sha256,                   # checksum_sha256
        now, now,                 # first_seen_at, last_seen_at
    ))
    if v3r:
        tag_rows.append((path, sha256, v3r))  # resolve audio_file_id after insert

audio_sql = """
    INSERT INTO public.audio_file
        (owner_user_id, file_key, path, filename, size_bytes, duration_s,
         bitrate_kbps, codec, checksum_sha256, first_seen_at, last_seen_at)
    VALUES %s
    ON CONFLICT (owner_user_id, file_key) DO UPDATE SET
        checksum_sha256 = EXCLUDED.checksum_sha256,
        path = EXCLUDED.path, filename = EXCLUDED.filename,
        size_bytes = EXCLUDED.size_bytes, duration_s = EXCLUDED.duration_s,
        last_seen_at = EXCLUDED.last_seen_at, updated_at = now()
    RETURNING id, file_key
"""

# 4. Insert audio_file, collect id map
file_key_to_id = {}
with pg.cursor() as cur:
    for i in range(0, len(audio_rows), BATCH):
        result = execute_values(cur, audio_sql, audio_rows[i:i+BATCH], fetch=True)
        file_key_to_id.update({fk: aid for aid, fk in result})

    # 5. Upsert dj_tag for rows with v3 metadata
    dj_tag_rows = []
    for path, sha256, v3r in tag_rows:
        afid = file_key_to_id.get(f"sha256:{sha256}")
        if not afid: continue
        dj_tag_rows.append((
            OWNER, afid,
            v3r.get("canonical_artist"), v3r.get("canonical_title"),
            v3r.get("canonical_album"), v3r.get("canonical_label"),
            v3r.get("canonical_catalog_number"),
            v3r.get("canonical_release_date"), v3r.get("canonical_year"),
            float(v3r["canonical_bpm"]) if v3r.get("canonical_bpm") else None,
            v3r.get("canonical_key"), v3r.get("canonical_genre"),
            v3r.get("canonical_sub_genre"), v3r.get("canonical_isrc"),
            v3r.get("energy"), v3r.get("dj_set_role"),
            False,  # manual_override
        ))

    if dj_tag_rows:
        execute_values(cur, """
            INSERT INTO public.dj_tag
                (owner_user_id, audio_file_id, artist, title, album, label,
                 catalog_number, release_date, year, bpm, musical_key,
                 canonical_genre, canonical_subgenre, isrc, energy, role, manual_override)
            VALUES %s
            ON CONFLICT (owner_user_id, audio_file_id) DO UPDATE SET
                bpm = EXCLUDED.bpm, musical_key = EXCLUDED.musical_key,
                canonical_genre = EXCLUDED.canonical_genre, updated_at = now()
        """, dj_tag_rows)

pg.commit()
pg.close()
print(f"Done: {len(audio_rows)} audio_file rows, {len(dj_tag_rows)} dj_tag rows")
```

Run: `cd hag/tools && python populate_audio_file.py`

---

### Phase 1 — Apple MU sidecars → apple_track_analysis (after Phase 0)

**What exists and what it does:**
- `hag/tools/apple_mu_analyses/<sha256>.json` — 2,621 sidecars, more arriving from `run_mu_scan.py`
- `hag/tools/taghag_import/apple_music_adapter.py` → `run_apple_music_ingestion()` — **this is a live FLAC analyzer** (calls Swift binary, re-hashes files from disk). It is NOT a sidecar reader. Do not use it for bulk sidecar ingest.
- `hag/tools/taghag_import/apple_derived_features.py` → `compute_derived_features(raw_json)` — pure math on MU JSON, reuse this.

**Write `hag/tools/ingest_mu_sidecars.py`** — reads the pre-computed sidecars, uses the same helper functions:

```python
#!/usr/bin/env python3
"""Ingest pre-computed Apple MU sidecars into Supabase. Idempotent."""
import json, hashlib, os, sys
from pathlib import Path
from taghag_import.config import read_database_config
from taghag_import.db_client import TaghagDbClient
from taghag_import.apple_derived_features import compute_derived_features
# Also import the private helpers from apple_music_adapter for JSON parsing:
from taghag_import.apple_music_adapter import (
    _downsample_array, _cmtime_ms, _range_ms, _activity_values,
    _loudness_scalar, _canonical_json_bytes
)

SIDECARS_DIR = Path(__file__).parent / "apple_mu_analyses"
OWNER = os.environ["TAGHAG_OWNER_USER_ID"]

config = read_database_config()
client = TaghagDbClient(config)

# Build sha256 → audio_file_id map (query Supabase once)
# GET /rest/v1/audio_file?select=id,checksum_sha256&checksum_sha256=not.is.null
# Build dict: sha256 → id

def get_sha256_to_id_map():
    rows = client._get_postgrest_rows("audio_file", {
        "select": "id,checksum_sha256",
        "checksum_sha256": "not.is.null",
        "owner_user_id": f"eq.{OWNER}",
    })
    return {r["checksum_sha256"]: r["id"] for r in rows if r.get("checksum_sha256")}

sha_to_id = get_sha256_to_id_map()

# Get already-ingested source_artifact_sha256 values (skip these)
done = {
    r["source_artifact_sha256"]
    for r in client._get_postgrest_rows("apple_analysis_runs", {
        "select": "source_artifact_sha256",
        "owner_user_id": f"eq.{OWNER}",
    })
}

for sidecar in sorted(SIDECARS_DIR.glob("*.json")):
    file_sha256 = sidecar.stem  # filename IS the file_hash_sha256
    audio_file_id = sha_to_id.get(file_sha256)
    if not audio_file_id:
        continue  # file not in library

    raw = json.loads(sidecar.read_text())
    payload_sha256 = hashlib.sha256(
        json.dumps(raw, sort_keys=True, separators=(",",":")).encode()
    ).hexdigest()

    if payload_sha256 in done:
        continue  # already ingested

    # apple_analysis_runs row (raw JSON archive)
    client._postgrest_request("apple_analysis_runs", [{
        "owner_user_id": OWNER,
        "audio_file_id": audio_file_id,
        "source_artifact_sha256": payload_sha256,
        "source_path": str(sidecar),
        "analyzer": "apple_music_understanding",
        "analyzer_version": raw.get("meta", {}).get("version", "unknown"),
        "raw_result_json": raw,
        "computed_at": "now()",
    }], on_conflict="audio_file_id,source_artifact_sha256")

    # apple_track_analysis row
    # Key fields from raw MU JSON:
    rhythm = raw.get("rhythm", {})
    key_data = raw.get("key", {})
    key_ranges = key_data.get("ranges", [])
    first_key = key_ranges[0].get("value", {}) if key_ranges else {}
    loudness = raw.get("loudness", {})
    instrument_activity = raw.get("instrumentActivity", {}).get("activity", {})

    client._postgrest_request("apple_track_analysis", [{
        "owner_user_id": OWNER,
        "audio_file_id": audio_file_id,
        "source_artifact_sha256": payload_sha256,
        "global_bpm": rhythm.get("beatsPerMinute"),
        "key_tonic": first_key.get("tonic"),
        "key_mode": first_key.get("mode"),
        "pace_curve": raw.get("pace", {}).get("ranges", []),
        "drum_activity": instrument_activity.get("drum") or instrument_activity.get("drums"),
        "bass_activity": instrument_activity.get("bass"),
        "vocal_activity": instrument_activity.get("vocal") or instrument_activity.get("vocals"),
        "loudness_integrated": loudness.get("integrated", {}).get("value"),
        "loudness_peak": loudness.get("peak", {}).get("value"),
        "loudness_momentary": loudness.get("momentary", []),
        "computed_at": "now()",
    }], on_conflict="audio_file_id,source_artifact_sha256")

    # apple_derived_features row (uses existing compute_derived_features)
    features = compute_derived_features(raw)
    client._postgrest_request("apple_derived_features", [{
        "owner_user_id": OWNER,
        "audio_file_id": audio_file_id,
        "source_artifact_sha256": payload_sha256,
        **{k: v for k, v in features.items() if v is not None},
        "computed_at": "now()",
    }], on_conflict="audio_file_id,source_artifact_sha256")

    print(f"  ✓ {sidecar.stem[:16]}… bpm={rhythm.get('beatsPerMinute')} key={first_key}")
    done.add(payload_sha256)
```

Run: `cd hag/tools && python ingest_mu_sidecars.py`
Re-run any time — idempotent via `source_artifact_sha256` dedup.

---

### Phase 2 — Automix payloads → track_analysis (after Phase 0, parallel with Phase 1)

No existing script. Write `hag/tools/ingest_automix.py`:

```python
#!/usr/bin/env python3
"""Ingest Echo Nest / Spotify Audio Analysis payloads into track_analysis."""
import json, os
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

PAYLOADS_DIR = Path(__file__).parent / "automix_payloads"  # ~31,822 <spotify_id>.json
V3_DB = os.path.expanduser("~/Projects/tag/slut_db/FRESH_2026/music_v3.db")
OWNER = os.environ["TAGHAG_OWNER_USER_ID"]
PG_URL = os.environ.get("TAGHAG_DB_POSTGRES_URL") or os.environ["DB_POSTGRES_URL"]

import sqlite3
# Build spotify_id → file_hash_sha256 via v3 track_identity
v3 = sqlite3.connect(f"file:{V3_DB}?mode=ro", uri=True)
spotify_to_sha = dict(v3.execute(
    "SELECT spotify_id, content_sha256 FROM track_identity "
    "WHERE spotify_id IS NOT NULL AND content_sha256 IS NOT NULL"
).fetchall())
v3.close()
# ~23,146 rows in v3 with both; the remaining ~8k payloads have no library match → skip

pg = psycopg2.connect(PG_URL)

# Build sha256 → audio_file_id from Supabase
with pg.cursor() as cur:
    cur.execute(
        "SELECT id, checksum_sha256 FROM public.audio_file "
        f"WHERE owner_user_id='{OWNER}' AND checksum_sha256 IS NOT NULL"
    )
    sha_to_afid = {sha: aid for aid, sha in cur.fetchall()}

rows = []
for payload_path in PAYLOADS_DIR.glob("*.json"):
    spotify_id = payload_path.stem
    sha256 = spotify_to_sha.get(spotify_id)
    if not sha256: continue
    afid = sha_to_afid.get(sha256)
    if not afid: continue

    p = json.loads(payload_path.read_text())
    t = p.get("track", {})
    energy = t.get("energy", 0.0) or 0.0
    valence = t.get("valence", 0.0) or 0.0
    dance = t.get("danceability", 0.0) or 0.0

    rows.append((
        OWNER, afid,
        "echonest_v1",             # schema_name
        "spotify_audio_analysis",  # model_profile
        json.dumps({}),            # models_json
        payload_path.stem,         # source_artifact_sha256 (spotify_id as proxy)
        str(payload_path),         # source_path
        json.dumps({}),            # genres_json
        valence,                   # happy (valence = positiveness)
        energy * (1.0 - valence),  # aggressive (high energy + low valence)
        1.0 - valence,             # relaxed
        energy,                    # party
        dance,                     # danceability
        json.dumps(p),             # raw_json
    ))

with pg.cursor() as cur:
    execute_values(cur, """
        INSERT INTO public.track_analysis
            (owner_user_id, audio_file_id, schema_name, model_profile, models_json,
             source_artifact_sha256, source_path, genres_json,
             happy, aggressive, relaxed, party, danceability, raw_json, computed_at)
        VALUES %s
        ON CONFLICT (owner_user_id, audio_file_id, schema_name) DO UPDATE SET
            happy=EXCLUDED.happy, aggressive=EXCLUDED.aggressive,
            relaxed=EXCLUDED.relaxed, party=EXCLUDED.party,
            danceability=EXCLUDED.danceability, raw_json=EXCLUDED.raw_json,
            updated_at=now()
    """, rows)
pg.commit()
pg.close()
print(f"Inserted {len(rows)} track_analysis rows (echonest_v1)")
```

Run: `cd hag/tools && python ingest_automix.py`

---

### Phase 3 — MIK → dj_tag supplement (after Phase 0)

**What exists and what it does:**
`hag/tools/taghag_import/mik_xml_adapter.py` — reads MIK energy cue points and BPM from a **Rekordbox XML export** (`downloaded.xml`). Single-track lookup by artist+title string match. This is for the real-time cue pipeline, not bulk ingest.

**Use Collection11.mikdb directly.** Write `hag/tools/ingest_mik.py`:

```python
#!/usr/bin/env python3
"""Bulk-ingest MIK BPM/key/energy/LUFS + cue points from Collection11.mikdb."""
import sqlite3, os, json
import psycopg2
from psycopg2.extras import execute_values

MIK_DB = os.path.expanduser(
    "~/Library/Application Support/Mixedinkey/Collection11.mikdb"
)
OWNER = os.environ["TAGHAG_OWNER_USER_ID"]
PG_URL = os.environ.get("TAGHAG_DB_POSTGRES_URL") or os.environ["DB_POSTGRES_URL"]

mik = sqlite3.connect(f"file:{MIK_DB}?mode=ro", uri=True)
mik.row_factory = sqlite3.Row

# Check actual path format in MIK before assuming prefix
sample = mik.execute("SELECT ZPATHSTRING FROM ZSONG LIMIT 5").fetchall()
print("MIK sample paths:", [r[0] for r in sample])

songs = mik.execute(
    "SELECT Z_PK, ZPATHSTRING, ZTEMPO, ZKEY, ZENERGY, ZVOLUMELUFS FROM ZSONG "
    "WHERE ZPATHSTRING IS NOT NULL"
).fetchall()

pg = psycopg2.connect(PG_URL)
with pg.cursor() as cur:
    cur.execute(
        "SELECT id, path FROM public.audio_file "
        f"WHERE owner_user_id='{OWNER}'"
    )
    path_to_afid = {p: aid for aid, p in cur.fetchall()}

def normalize_mik_path(p):
    # MIK may store /Volumes/MUSIC/... or /Users/g/... — check sample output above
    # Adjust prefix normalization once you see actual paths
    return str(p).strip()

tag_rows, cue_rows = [], []
pk_to_afid = {}

for row in songs:
    path = normalize_mik_path(row["ZPATHSTRING"])
    afid = path_to_afid.get(path)
    if not afid:
        continue
    pk_to_afid[row["Z_PK"]] = afid
    energy_val = row["ZENERGY"]
    tag_rows.append((
        OWNER, afid,
        float(row["ZTEMPO"]) if row["ZTEMPO"] else None,  # bpm
        row["ZKEY"],                                       # musical_key
        str(int(energy_val)) if energy_val else None,      # energy (e.g. "7")
        float(row["ZVOLUMELUFS"]) if row["ZVOLUMELUFS"] else None,  # stored in notes
        "mik",                                             # tag_source
        False,                                             # manual_override
    ))

# Cue points
all_pks = list(pk_to_afid.keys())
for chunk_start in range(0, len(all_pks), 500):
    pks = all_pks[chunk_start:chunk_start+500]
    placeholders = ",".join("?" * len(pks))
    for cue in mik.execute(
        f"SELECT ZSONG, ZPOSITION, ZNAME, ZCOLOR FROM ZCUEPOINT WHERE ZSONG IN ({placeholders})",
        pks
    ):
        afid = pk_to_afid.get(cue["ZSONG"])
        if not afid: continue
        cue_rows.append((
            OWNER, afid,
            cue["ZNAME"],                    # name
            int(cue["ZPOSITION"] * 1000),    # time_ms (ZPOSITION is seconds)
            cue["ZCOLOR"],                   # color
            "hot_cue",                       # cue_type
            "mik",                           # source_system
            1.0,                             # confidence
            "file",                          # time_base
        ))

mik.close()

with pg.cursor() as cur:
    execute_values(cur, """
        INSERT INTO public.dj_tag
            (owner_user_id, audio_file_id, bpm, musical_key, energy, notes, tag_source, manual_override)
        VALUES %s
        ON CONFLICT (owner_user_id, audio_file_id) DO UPDATE SET
            bpm=COALESCE(EXCLUDED.bpm, dj_tag.bpm),
            musical_key=COALESCE(EXCLUDED.musical_key, dj_tag.musical_key),
            energy=COALESCE(EXCLUDED.energy, dj_tag.energy),
            updated_at=now()
    """, tag_rows)

    if cue_rows:
        execute_values(cur, """
            INSERT INTO public.track_cue
                (owner_user_id, audio_file_id, name, time_ms, color,
                 cue_type, source_system, confidence, time_base)
            VALUES %s
            ON CONFLICT DO NOTHING
        """, cue_rows)

pg.commit()
pg.close()
print(f"MIK: {len(tag_rows)} dj_tag rows, {len(cue_rows)} track_cue rows")
```

**Before running:** print the sample paths and verify the prefix normalization against `audio_file.path`. MIK paths may differ from MASTER_LIBRARY paths in minor ways (trailing slash, symlink resolution).

Run: `cd hag/tools && python ingest_mik.py`

---

### Phase 4 — Rekordbox → dj_tag + cues (after Phase 0)

```
~/Library/Pioneer/rekordbox/master.db  — LOCKED while RBX is running
~/Library/Pioneer/rekordbox/master.backup.db  — readable now
```

Check backup schema: `sqlite3 ~/Library/Pioneer/rekordbox/master.backup.db ".tables"` — look for `djmdContent` and `djmdCue`.

Write `hag/tools/ingest_rekordbox.py` — same pattern as MIK:
- `djmdContent`: `FolderPath` (path), `BPM`, `Tonality` (key), `ColorID`, `StarsRating`
- `djmdCue`: `InTrackID`, `Kind` (0=cue,1=loop), `InMsec` (position ms), `ColorID`, `Comment`

Join: `djmdContent.FolderPath` → normalize → `audio_file.path`

Tag source: `'rekordbox'`. Merge into `dj_tag` with `COALESCE` (don't overwrite MIK values if already set).

---

### Phase 5 — Re-seat 744 orphaned track_embedding rows (after Phase 0)

```sql
-- Check what keys the orphaned rows carry:
SELECT id, source_artifact_sha256, source_analysis_id, vector_schema
FROM public.track_embedding
LIMIT 5;

-- Then update:
UPDATE public.track_embedding te
SET audio_file_id = af.id
FROM public.audio_file af
WHERE te.audio_file_id IS NULL  -- or points to a non-existent id
  AND af.checksum_sha256 = te.source_artifact_sha256
  AND af.owner_user_id = te.owner_user_id;
```

If `source_artifact_sha256` doesn't map directly to file SHA256, check what it references (it may point to an `apple_analysis_runs.source_artifact_sha256` which is the JSON payload hash, not the file hash). Trace the chain before updating.

---

## B. Spotify-AA artist + collab graph  (slut repo — run from `~/Projects/tag/slut`)

This writes to `music_v4.db`, which is the slut side's jurisdiction (DECISIONS_LOCKED §5). Run these from the slut repo, not from hag.

**Current state:** Beatport layer done (6,470 artists, 2,435 collab edges, 15,771 track-artist links). Spotify-AA layer: tools written, parquet downloaded, never executed.

```
/Volumes/ATTIC/kaggle-data/spotify-aa/
  tracks.parquet       — ISRC + spotify_id + album_id + duration
  artists.parquet      — spotify_artist_id + name + popularity + followers
  track_artists.parquet — rowid join table (track_rowid → artist_rowid)
Total: 24G (already on disk)
```

**Step 1 — slice parquet to library ISRCs (~5–10 min, needs duckdb):**
```bash
cd ~/Projects/tag/slut
pip install duckdb  # if not present
python tools/v4/aa_parquet_to_sqlite.py \
  --aa /Volumes/ATTIC/kaggle-data/spotify-aa \
  --v4 ~/Projects/tag/slut_db/FRESH_2026/music_v4.db \
  --out /tmp/aa_slice.sqlite
```
Reads v4 ISRCs, filters ~148GB parquet to ~15k matching rows, resolves artist_ids JSON inline, emits `aa_slice.sqlite`. Read-only on parquet + v4; only writes `/tmp/aa_slice.sqlite`.

**Step 2 — ingest into v4 (~1–2 min):**
```bash
python tools/v4/ingest_spotify_reference.py extract \
  --aa /tmp/aa_slice.sqlite \
  --v4 ~/Projects/tag/slut_db/FRESH_2026/music_v4.db
```
Builds: `ref_spotify_track`, `ref_spotify_artist`, `ref_track_artist`, and artist-artist co-credit collab edges (same `(artist_a, artist_b, weight)` shape as `ref_bp_collab`). Read the script first to confirm it snapshots before writing.

**Step 3 — promote to first-class artist/track_artist:**
```bash
python tools/v4/promote_artists.py \
  --v4 ~/Projects/tag/slut_db/FRESH_2026/music_v4.db
```
Adds Spotify-AA artists + track-artist links to the `artist` and `track_artist` tables (Beatport side already there). Merged collab graph gives artist-artist edges across both sources.

**After:** `artist` will have Beatport 6,470 + Spotify-AA additions; `ref_bp_collab` + new Spotify-AA edges give a full queryable artist-artist relationship graph for the library.

Needs `/Volumes/ATTIC` access (Desktop Commander if in sandboxed env).

---

## Execution order

```
[rotate Supabase key]
        ↓
Phase 0: populate_audio_file.py  (~3–5 min)
        ↓
Phase 1: ingest_mu_sidecars.py   ┐
Phase 2: ingest_automix.py       ├── parallel, all after Phase 0
Phase 3: ingest_mik.py           │
Phase 4: ingest_rekordbox.py     ┘
        ↓
Phase 5: re-seat track_embedding  (SQL, ~1 min)

[separately, in slut repo]
Step 1: aa_parquet_to_sqlite.py → /tmp/aa_slice.sqlite
Step 2: ingest_spotify_reference.py extract
Step 3: promote_artists.py
```
