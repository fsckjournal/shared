# WEEKLY PLAN — tag project (lightweight PCM) — week of 2026-07-11

_Living current-week snapshot; overwritten each Monday, history in git. Grounded in the
record consolidated by this run (rem sync → spine #194 / shared @036646c). Capture inbox
file EMPTY this run (header only), but ONE live capture folded in from operator direction this session:
membership-console → slut-lane, rebuild in Claude Design (obj. + milestone 7, source=capture). No invented
metrics — every KPI carries its live query as means-of-verification._

**HEADLINE: KILL V3.** v3 is **still live** — all 5 blockers uncleared (verified in code
2026-07-11). Track pass/fail, not burndown.

---

## 1. Objectives (logframe)

| Hierarchy of Objectives | KPI | Means of Verification | Risk / Assumption | Source |
|---|---|---|---|---|
| **GOAL: v3 dead** | v3 still live? **Y** | intake.py:2521 + 4 hag crosswalk refs + parity script all live | Never mark dead until (2)∧(3) provably off v3 | record |
| ├ Purpose: intake writes v4 (#2) | append-only bridge exists? **N** | `intake.py:2521` `_stage_redirect_v3_schema`→`music_v3.db` | v4 must be reproducible FIRST (spec §6 Q5) | record |
| ├ Purpose: brain re-keyed off v3 (#3) | crosswalk refs = **4** | `grep crosswalk_v3v4_identity hag/*.py` | naive v3-full-SHA re-key diverges ~91% | record |
| ├ Purpose: parity neutralized (#4) | parity scripts = **4** (1+3 wt) | `find -iname validate_v3_dual_write_parity.py` | worktree copies must all go | record |
| └ Purpose: views regen + delete (#5) | done? **N** (gated on 2+3) | — | copy→verify→delete, never before 2+3 | record |
| **Provider-gap closure** | bp_gap **4,851** / spot_gap **627** | live query (mix-set ∧ ISRC ∧ no ref) | gap def differs from #158 worklist (see KPI note) | record |
| **Library integrity** | 64 masters redownload / fp 99.6% | integrity_v1.db + fingerprints_v1.db | corrupt = re-acquire only, NEVER delete | record |
| **Record hygiene** | 29 open Q / 18 ⛔ / 5 locked this wk | handoff-tail --open; git log | stale-opens must be reconciled vs ledger | record |
| **Land stranded fix** | 74c4a94b on dev? **N** | `git branch --contains 74c4a94b` = worktree only | verified fix marooned on isolated worktree | record |
| **Membership console → slut-lane, Claude-Design rebuild** | writes §17 enum on wip copy? **N** (retire Swift app) | `membership-console/Sources/*.swift` (standalone, unversioned) | UI = operator lane (Claude Design); I land the data contract only | **capture** |

---

## 2. KPI variance (last → this → target; pulled live this run)

| KPI | Last (record) | This (live 2026-07-11) | Target | Status |
|---|---|---|---|---|
| **v3 still live? (headline)** | Y | **Y** | N | 🔴 halt-gate: 5 blockers open |
| — (2) intake off v3 | v3-native | **v3-native** (intake.py:2521) | v4-native | 🔴 HARD BLOCKER |
| — (3) brain re-key | 4 refs | **4 refs** (pool_v2/build_pool/overlap_report/list_columns) | 0 | 🔴 |
| — (4) neutralize parity | 4 files | **4 files** (slut/scripts +3 wt) | 0 | 🟡 mechanical |
| — (5) view regen + delete | not started | **not started** | done | ⚪ gated on 2+3 |
| Beatport refs | 17,548 (#158)→17,920 (#187) | **17,921** | — | 🟢 steady-state via §19 |
| Spotify refs | 22,882→24,274 (#158) | **24,363** | — | 🟢 |
| bp gap (mix∧ISRC∧no-ref) | — (first live) | **4,851** | 0 | 🟡 needs Lexicon export loop |
| spotify gap | — (first live) | **627** | 0 | 🟡 |
| Fingerprint coverage | 99.6% (#182) | **30,384/30,507 = 99.6%** | ~100% | 🟢 |
| Corrupt/truncated masters | 64 (#186) | **64** (44 corrupt+20 trunc) | 0 (redownload) | 🟡 operator re-acquire |
| Membership mix/listen/uncl | 24,529/4,745/2,171 (#148) | **24,529/4,745/2,171** | — | 🟢 stable |
| Open recording-clusters #167 | 78 HELD | **78 HELD, 72 classified r/o** (7 DO-NOT-MERGE) | operator-ruled | 🟡 read-only, unapplied |
| Open spine questions | — (first) | **29** (18 ⛔ needs) | trending ↓ | 🟡 |
| Decisions locked this week | — | **5** (§15/§11e/§19/§C17/§17+18) | — | 🟢 |
| Persona/skill drift fixed | — | **2** (advisor.md pushed; advisor SKILL 2 path fixes) | 0 residual | 🟢 |

**KPI note (advisor bar — don't echo a stale number):** my live gap (bp 4,851 / spot 627)
is scoped `membership='mix' ∧ isrc present ∧ no provider ref`. STATE's "~7,372 Beatport /
973 Spotify" (#158/#187) used the gap-closer's own worklist base (all owned, incl. non-mix).
Different denominators — NOT reconciled to one number; both cited with their query. The
`mix`-scoped figure is the right target for the automix pool.

---

## 3. This week's milestones + dependencies (ordered, gated)

1. **Land stranded `ts-get` fix `74c4a94b`** (title-aware batch-root selection, verified) from
   `worktree-listen-flag-v4-bridge` → **dev**. Operator was mid-`merge with dev` (interrupted,
   plan mode). **Dep:** none. **Needs operator GO** (merge vs cherry-pick). _Low-risk, do first._
2. **v3-kill (2) — append-only content_sha256 bridge** so intake writes v4. **Dep:** v4
   reproducibility (spec §6 Q5) FIRST; then identity_resolver.py sha-first. **Needs operator GO**
   (this is the headline path; multi-phase). Plan: `~/.claude/plans/shimmering-mixing-stonebraker.md`.
3. **⭐ Run `library_hygiene_audit_prompt.md`** (armed, read-only, whole-library census; arms the
   nuclear canonicalization). **Dep:** none — read-only, no gate to RUN. Output = decision surface.
4. **Provider gap → 0:** hand operator M3U of still-unmatched `mix` masters
   (`slut/output/still_unmatched_{beatport,spotify}.m3u8`) → his Lexicon export loop. **Operator manual.**
5. **Corrupt masters (64):** operator re-acquire from `corrupt_masters_REVIEW.csv` (51 have intact
   head-fp for acoustic-twin sweep first; 13 hard-redownload). **Operator manual, NEVER delete.**
6. **v3-kill (4) — neutralize `validate_v3_dual_write_parity.py`** (+3 wt copies). Mechanical;
   can land anytime, independent of 2/3. **Needs operator GO.**

7. **Membership console → slut-lane, rebuild in Claude Design** _(capture-sourced, this week)_.
   Retire the standalone Swift app (`~/Projects/tag/membership-console`, unversioned, `SQLITE_OPEN_READWRITE`
   on a wip copy, writes mocked). **UI/UX = operator lane (Claude Design) — not mine to build.** My
   backbone deliverable = the **data contract** the redesign must honor: reads `track` + writes
   `track.membership` **enum `mix`/`listen`/`unclassified`** (§17, spine #134/#148 — NOT the app's stale
   `pool`/`iceberg` + `membership(scope,scope_key,class)` shape), always on a gated `music_v4.membership_wip.db`
   copy, editing the upstream intent field so **downstream views regenerate** (never edit a view). **Dep:**
   none to start the contract; **operator drives the design.** Lane basis: §5 (v4 sole writer = slut) + §17.

**v3-kill prerequisite (CORRECTED — I first mis-filed this as scope-creep):** the MIK no_waveform
*flag* is a weak corruption signal (#194: 0 net-new corrupt beyond #186's 64), BUT the *stub/corrupt-
preferred-master finding* is **load-bearing and IS a blocker-(2) prerequisite**: the append-only bridge
must not canonicalize new intake onto a track whose preferred master is a 15s stub / truncated file
(the resolver would attach to garbage). Gate the bridge on the 64-row `corrupt_masters_REVIEW.csv` set.
See v3_kill_prompt.md blocker (2). — The 5,741 nightly "missing" (#192/#193) IS a genuine scope-creep
trap: verifier path-contract false-alarm, not data loss — fix the verifier, don't chase files.

---

## 4. Risks + one-line retro

**Phase-1 assumptions no longer holding:**
- **§15 "v4 is inert / out-of-runtime-path"** — SUPERSEDED 2026-07-11 (#189/#190). v4 is now the
  SOLE canonical store. Any session still booting from the v4-inert framing is wrong.
- **"purple Finder tags = live membership signal"** — consumed by the MUSIC→ICEBERG drain (#135);
  membership now backfills from location + primary-artist, not tags.

**Biggest workflow bottleneck:** background/agent sessions auto-isolate into git worktrees, stranding
verified fixes on branches that never reach `dev` (this week: `74c4a94b` + the near-miss report needed
a manual cherry-pick dance). **Systemic fix:** give agent sessions a standing "land-to-dev" step (or
work on a normal feature branch, not an auto-worktree) so a verified fix is never one forgotten
cherry-pick away from being lost.

**Retro (one line):** the record is healthy and moving (v4-sole ratified, membership + provider refs
landed on real v4) — the drag is not analysis, it's *landing* finished work past worktree isolation
and operator-GO gates.

---

## UNSURE — questions for Georges (not guessed; would reverse a decision or declare v3 dead)
- **v3-kill sequencing:** build the append-only bridge (#2) this week, or land the mechanical
  parity-neutralize (#4) + brain re-key (#3) first? Record says #2 needs v4-reproducibility (Q5)
  as prereq — confirm you want Q5 scoped in before the bridge, or the bridge deferred again.
- **Stranded `74c4a94b`:** merge the whole `listen-flag-v4-bridge` worktree to dev, or cherry-pick
  just the fix? (The gu_nubreed8 masters remediation on that branch is still gated/unexecuted.)
- **Provider gap target:** close to 0 on the `mix`-scoped 4,851/627, or the wider #158 worklist?
  (Decides which M3U I generate.)
