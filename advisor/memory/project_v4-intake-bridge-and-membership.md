---
name: v4-intake-bridge-and-membership
description: State of --mix/--listen membership + the decided v4 intake bridge (spine #134/#141/#145/#148/#150/#152); what's done vs blocked as of 2026-07-10
metadata:
  type: project
---

`track.membership` (pool intent: mix/listen/unclassified) and the `--mix`/`--listen` intake flags.

**Done (2026-07-10):** Part 1 backfill LANDED on real music_v4.db. `apply_membership_v2.py --apply` (#148)
set the enum to mix/listen/unclassified (#134 rename work→mix, iceberg→listen) + ran the #140
primary-artist resolver. Current: mix 24,529 / listen 4,745 / unclassified 2,171 (1,101 off_disk +
1,070 no_primary_140_unresolved). Do NOT re-run the rename/backfill.

**Blocked (spine #150→#152):** the `--mix`/`--listen` CLI flag (#141 Part 2) is UNBUILT. Root cause:
intake is v3-native — `get-intake`/`ts-stage` write music_v3.db and refuse v4 (intake.py:2478-2547).
`track.membership` is v4-only, so a fresh `ts-get <album> --listen` creates no v4.track row to stamp
and errors `rc=2` (unknown flag forwarded to qobuz-dl).

**Decided approach (do NOT re-derive):** `docs/v4/2026-07-03-v4-intake-write-contract-spec.md` §6
(Fable review) chose an APPEND-ONLY content_sha256 bridge — make migrate_v3_to_v4.py append-only,
keep intake v3-native, v3 stays source of truth, v4 rederivable. Full port AND dual-write both
REJECTED. §6 order: (1) make v4 reproducible FIRST (#1 priority, live DB not rebuildable from repo);
(2) identity_resolver.py sha-first match-or-create (standalone, tested); (3) append-only bridge behind
--v4-intake; (4) album-grain flag writes track.membership (reuse enum CHECK from apply_membership_v2
but NOT its 31445-guard, which aborts once the bridge adds rows).

**Why:** operator wants `ts-get <album> --listen` to tag membership at album grain (#141). Approved plan:
/Users/g/.claude/plans/shimmering-mixing-stonebraker.md.

**How to apply:** this is a multi-phase build in progress. NEVER conflate track.membership (pool intent)
with release_package_member (migration 0030 / compilation-slot axis) — different table/enum/writer.
See [[radical-collapse-and-hazards]]. Believe his flag usage is intentional; see
[[dont-dismiss-sanctioned-flags]].
