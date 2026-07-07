# PLAN — supersede XML-first-cue energy with MIK-DB ZENERGY

**Owner:** hag lane. **Status:** ready to run. **Spine:** #99 (open question this closes).
**Written:** 2026-07-07 by Claude, for whoever runs next (Gemini or Claude).

This is a **fool-proof, copy-paste** plan. Every step says exactly what to run and what
you should see. Nothing here writes to `music_v3.db`/`music_v4.db` (slut's lane) or to
`audio_file`. It only adds `mik`-source rows to `dj_tag`. Fully reversible.

---

## Background (why this exists — 30 sec)

Overnight 2026-07-07, energy got backfilled into `dj_tag.energy` (26,285 tracks) BUT via
a shortcut: the *first* `Energy N` cue from `master.xml`. The record (DECISIONS_LOCKED
§12, spine #47) says the sanctioned source is **MIK `Collection11.mikdb` `ZSONG.ZENERGY`**,
not the XML (operator: "that xml is garbage"). This plan replaces/augments the XML values
with the real MIK-DB scalar, kept on separate `tag_source='mik'` rows so nothing is
destroyed.

**Unresolved contradiction the script resolves for you:** spine #48 says the MIK DB has
only **~2,101** tracks with ZENERGY; the Gemini session claimed **~33,596**. The script
PROBES and prints the true number *before* writing. That number decides everything:
- **~2,101** → MIK-DB energy is a small enrichment; KEEP the 26,285 XML values as the gate.
- **~31k** → MIK-DB energy SUPERSEDES the XML values; retire them afterward.

Do not skip the probe. Do not assume which world you're in.

---

## Step 0 — preconditions (10 sec)

```bash
cd ~/Projects/tag/hag
test -f "$HOME/Library/Application Support/Mixedinkey/Collection11.mikdb" && echo "MIK DB present" || \
  find ~/Library -iname 'Collection11.mikdb' 2>/dev/null   # if not at the default path
grep -q TAGHAG_SUPABASE_SECRET_KEY .env && echo ".env key present"
python3 -c "import requests" 2>/dev/null || pip3 install requests --break-system-packages
```
Expect: "MIK DB present" and ".env key present". If the DB is elsewhere, pass
`--mikdb /full/path` to every command below.

## Step 1 — PROBE (no writes). This is the decision point.

```bash
python3 tools/backfill_energy_mikdb.py
```
Read the `[probe]` lines and the `=== VERDICT ===`. Key numbers:
- `ZSONG rows / with scalar ZENERGY(>0)` — resolves the 2,101-vs-33,596 question.
- `MIK-energy -> audio_file MATCHES (path-join)` — how many tracks this can actually fill.
- `WITHOUT any existing energy row` — net-new coverage beyond the 26,285 already there.

**STOP and decide** based on the verdict:
- verdict says SMALL (<5,000 matches) → this is enrichment. Proceed to Step 2 to add the
  high-fidelity rows, but do NOT retire the XML values (Step 4 stays skipped).
- verdict says LARGE (≥5,000) → proceed to Step 2, then Step 4 to retire XML values.

## Step 2 — smoke test the write (50 rows)

```bash
python3 tools/backfill_energy_mikdb.py --apply --limit 50
```
Then verify in Supabase (MCP `execute_sql` or the REST snippet the script prints):
```sql
select count(*), min(energy::int), max(energy::int)
from dj_tag where tag_source='mik' and energy is not null;
```
Expect ~50 rows, energy within 1..10. If it errors on the POST (missing column/constraint),
the script falls back automatically; if it still fails, the WARN lines tell you why —
most likely `dj_tag` requires `owner_user_id` (add `"owner_user_id": "<uuid>"` to the POST
payload; copy the uuid from any existing dj_tag row).

## Step 3 — full apply

```bash
python3 tools/backfill_energy_mikdb.py --apply
```
Verify:
```sql
select tag_source, count(*) filter (where energy is not null) e
from dj_tag group by tag_source order by e desc;
```

## Step 4 — (ONLY if verdict was LARGE) retire the XML-first-cue values

Do NOT run this if the probe said SMALL. This makes `mik` the sole energy source.
```sql
-- reversible: back up first
create table dj_tag_energy_xml_backup_20260707 as
  select id, audio_file_id, energy from dj_tag where tag_source='rekordbox_xml' and energy is not null;
update dj_tag set energy=null where tag_source='rekordbox_xml' and energy is not null;
```

## Step 5 — recompute the pool, update the record

```sql
-- pool with the new energy (fast form; avoids correlated-subquery timeout)
with mu as (select distinct audio_file_id id from apple_derived_features),
k as (select distinct audio_file_id id from dj_tag where key_camelot is not null),
e as (select distinct audio_file_id id from dj_tag where energy is not null),
b as (select distinct audio_file_id id from dj_tag where bpm is not null and tag_source='rekordbox_xml'),
s as (select distinct af.id from audio_file af
      join crosswalk_v3v4_identity c on c.v3_streaminfo_md5=af.streaminfo_md5
      where c.spotify_track_id is not null)
select (select count(*) from mu join k using(id) join e using(id) join b using(id) join s using(id)) all5;
```
Then append a spine note (uses git-safe-friendly tool, NOT raw git):
```bash
~/Projects/tag/shared/bin/handoff-append --from hag --to both --kind data-release \
  --re 99 --summary "MIK-DB ZENERGY backfill applied. Probe found <N> ZSONG energy rows, \
<M> path-joined to audio_file. Added <M> tag_source='mik' energy rows. XML values <kept|retired>. \
Pool now <P>. Supersedes the XML-first-cue energy of #99."
```

## Step 6 — commit (the pre-commit hook blocks raw git; use git-safe with explicit paths)

```bash
cd ~/Projects/tag/hag
~/Projects/tag/shared/bin/git-safe commit -m "feat(energy): MIK-DB ZENERGY backfill (supersede XML-first-cue, spine #99)" \
  tools/backfill_energy_mikdb.py

cd ~/Projects/tag/shared
~/Projects/tag/shared/bin/git-safe commit -m "docs: energy backfill audit + MIK-DB supersede plan (spine #99)" \
  knowledge/ENERGY_BACKFILL_AND_POOL_2026-07-07.md \
  knowledge/PLAN_mikdb_energy_supersede_2026-07-07.md \
  handoffs/handoff.jsonl
# push both when ready (shared push may need operator per AGENT.md):
#   git -C ~/Projects/tag/shared push   ;   git -C ~/Projects/tag/hag push
```

---

## Guardrails / gotchas (read before running)

- **The probe is the whole game.** If MIK ZENERGY coverage is small, you're enriching,
  not replacing — don't nuke the XML values.
- **Path-join fidelity.** Uses the same `parent_dir/filename_no_ext` casefold join proven
  for key_camelot/BPM (spine #85). If matches are surprisingly low, MIK may hold
  `ZBOOKMARKDATA` blobs instead of `ZPATHSTRING` — the script parses both; check the
  `unresolved paths` count in the probe.
- **`dj_tag` insert requirements.** If POST fails, the table likely needs `owner_user_id`
  (and maybe RLS off / service key — the script uses the service key already). Copy the
  owner uuid from an existing row.
- **Never touch v3/v4.** Energy is hag's measured lane (§12). This script only writes
  `dj_tag` in Supabase. `dj_admission` (the `admitted` override) lives in the CORRUPT
  `music_v3.db` — leave it until slut repairs v3 (memory: music-v3-db-corruption).
- **Reversible:** `delete from dj_tag where tag_source='mik';` undoes the whole thing.
