# PROMPT — Fold artist-name aliases in the v4 canonical artist layer [slut lane]

Self-contained handoff. Goal: dedupe **variant-spelling aliases** in v4 `public.artist`
(`promote_artists.py`), so the same act isn't two artist nodes. hag's brain mirror + the
automix collab graph inherit the fix on the next re-load (`outputs/load_artist_graph.py`, idempotent).

## Why (evidence)
The brain artist graph (mirrored from v4 2026-07-06, spine #92) surfaced duplicate artist
entities that are the **same artist under variant spellings** — they inflate the node set and
make an alias hop look like a collaboration to automix. Verify live; don't inherit on faith.

## The data — two buckets, only ONE is mergeable
Report: `shared/knowledge/artist_alias_candidates_2026-07-06.csv` (regenerable from v4 `artist`
+ `ref_artist_collab`/`ref_bp_collab`; name-norm = NFKD-fold diacritics, lowercase, strip
punctuation + `the/feat/ft/and/vs/pres`).

1. **`name_norm_collision` → MERGE (307 pairs / 279 groups / 571 artists).** Same artist, variant
   spelling: `Sven Väth`=`Sven Vath`, `Beyoncé`=`Beyonce`, `I:Cube`=`I-Cube`, `Léonie Pernet`=
   `Leonie Pernet`. Safe to collapse to one entity.
2. **`containment` → mostly KEEP (47 group/member + 24 review).** `Kraak & Smaak` vs `Kraak`/
   `Smaak`, `Lindstrøm & Prins Thomas` vs its members, `Woolfy vs. Projections` vs `Woolfy` —
   these are **distinct entities with a real collaboration**. Do NOT merge group↔member. The 24
   `REVIEW` rows need a human eye (some are true aliases like `Matthew Herbert`~`Herbert`,
   `Crazy P`~`Crazy Penis`).

## Approach (slut)
1. Extend `tools/v4/promote_artists.py` (or a dedup migration) to unify bucket-1 collisions:
   pick a canonical per group deterministically — prefer the node carrying `beatport_artist_id`
   (slut's provider), else higher `popularity`/`followers`, else the richest/NFC name — and
   repoint `track_artist` + the provider-id columns onto it; drop the losers. Keep both provider
   ids on the survivor if they differ.
2. Do NOT touch bucket-2 group/member pairs. Gate bucket-1 `REVIEW`/containment behind operator ack.
3. v4 is write-frozen (§15) → land this via the sanctioned migration path (mirror `0019`), not an
   ad-hoc write (spine #54).
4. Signal hag on completion (spine `data-release`) so hag re-runs `outputs/load_artist_graph.py`
   (idempotent upsert; the brain mirror + `artist_collab` + Roon views inherit the merge).

## Verify
Artist count drops by ~ (571 − 279) ≈ 292; 0 dangling `track_artist.artist_id`; a merged act
(e.g. Sven Väth) has one node with both provider ids; group/member pairs still two nodes.

Spine to cite: #54 (v4 single-writer), #92 (artist graph mirrored to brain).
