---
name: radical-collapse-and-hazards
description: The operator's standing ask — ONE db (v4 sole) + ONE intent-based membership field that generates every view — plus the live two-store hazards to surface on boot
metadata:
  type: project
---

**The radical collapse (operator-confirmed 2026-07-09).** Full spec: `slut/docs/decisions/RADICAL_COLLAPSE_one_db_one_membership.md`.

Two DISTINCT issues, same disease (two stores that disagree; agents reconcile instead of collapse). **Do NOT conflate them into "where are the files"** — that is the wrong axis and every past session made that error.
- **Issue A — membership.** Defined by **intent**, not disk location: *work-set* (electronic, mixable, gets Essentia/sidecars/payloads, needs Supabase mirror, needs a view where he sees ONLY these) vs *frozen/iceberg* (listening-only, never mixed, no analysis, out of sight). Disk location / purple tags / rekordbox visibility are downstream CONSEQUENCES, not the definition. Killer symptom proving A unsolved: he deletes an artist in rekordbox, they return a week later — because the edit is on a downstream *view*, not an upstream authoritative membership store.
- **Issue B — the DB.** v3 rotten (spine #97). v4 became a *shadow* instead of the final destination. Collapse to v4 sole.

**The cure:** ONE db (v4 sole; v3 dead — not bridged/synced/parity). ONE `membership` field (`work`/`iceberg`/`unclassified`) decided by intent, the SOURCE every view is generated from (mount, Essentia, Supabase one-way mirror of work-set, what rekordbox may see). Edit membership once upstream; every view regenerates; deletions stick. Supabase = one-way derived mirror, NEVER a second canonical store.

**Backfill** `[verified: /tmp/find_split.py, read-only vs v4 + both volumes, 2026-07-09]`: MASTER 25,649 / ICEBERG 4,695 / **BOTH 0** / NEITHER 1,101. BOTH=0 → drain physically coherent, disk gives a deterministic answer for 96.5% with no reconciliation. NEITHER=1,101 (910 still ISRC-anchored) = drift/missing → land `unclassified`, never guess. Evidence for intent = purple tags (#107) + ICEBERG-drain + disk + isrc + dj-eligibility; agreements auto-resolve, operator rules disagreement set once. Execute in Code on a COPY of v4, gated, never deleting masters.

**Live two-store hazards (re-check before trusting; the map rots):**
- Automix payloads split RIGHT NOW: `hag/automix_payloads` ~31.8k vs `hag/tools/automix_payloads` ~7.9k (a "merge" 4 days ago didn't hold). Collapse to one store.
- Playlist resolver reads the 314-row v3 husk (`track_identity/asset_file/asset_link`) not the 31k real `track`/`track_file` — add a guard that fails LOUDLY on the husk. (task_b349f2e9, ADR-0009 sign-off.)
- **Real DB = `music_v4.db`** (`~/Projects/tag/slut_db/FRESH_2026/`). `files`(314)/`asset_file`(318) = v3 HUSKS, never truth. v3 corrupt.
- Drained iceberg (ATTIC/ICEBERG 4,810) is back in Roon's scan (33,582). Decide if inert files should be Roon-served.
- Roon ID-vs-nonID ≈ ISRC-presence split (nonID: 0/11,906 have ISRC) — free external identity audit.

See [[move-dont-menu]], [[artist-identity-anchor]] (the separate artist axis), [[never-delete-masters]].
