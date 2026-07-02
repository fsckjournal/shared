# tag/shared — the handoff spine

One append-only, schema-validated, git-versioned event log that the **hag**
(brain) and **slut** (backbone) repos both read and write. It replaces the
brittle predecessors: date-stamped `HANDOFF_FROM_HAG_*.md` / `HANDOFF_TO_HAG_*.md`
files, pasted "Handoff Summary — for the next instance" blocks, and drifting
`SPRINT_STATUS.md` / authority docs.

## Why

Coordination between the two repos used to travel as **prose carried by a human**
between sessions and environments (local / web container / iPhone). It desynced
constantly — "drift"/"stale" show up thousands of times across past sessions, and
whole sessions dead-ended because a handoff assumed a `$TAGSLUT_DB` that wasn't
mounted. This spine makes handoffs **typed, ordered, durable, and machine-readable
by either agent without the human as courier.**

## Layout

```
shared/
  handoffs/handoff.jsonl      # append-only event log — the source of truth
  state/hag.json              # hag's current-state snapshot (last-writer-wins)
  state/slut.json             # slut's current-state snapshot
  schema/handoff.schema.json  # JSON Schema (draft-07) for one event
  bin/handoff-append          # validated, atomic writer (auto-fills ts/git/env)
  bin/handoff-tail            # reader — run this FIRST on every session resume
```

## Contract

- **Log is append-only.** Never edit or reorder past lines. Corrections are new events.
- **Every write goes through `bin/handoff-append`** so it is schema-checked and atomic.
- **`state/*.json` is a convenience snapshot, not history.** If it and the log
  disagree, the log wins.
- **`schema_version` is checked by readers.** Bump only on breaking changes.

## Usage

Resume (do this before touching anything):

```bash
tag/shared/bin/handoff-tail --to hag --open      # from a hag session
tag/shared/bin/handoff-tail --to slut --open     # from a slut session
```

Hand work over:

```bash
tag/shared/bin/handoff-append --from hag --to slut --kind handoff \
  --summary "Regenerated loudness handoff table; join on content_sha256." \
  --artifact tools/mixslice/loudness_handoff.parquet:hag \
  --open "On BPM disagreement >2%, which source wins?" \
  --session 12f336bd
```

Record a block instead of silently failing (this is the fix for the
"$TAGSLUT_DB unset, cannot run here" dead-ends):

```bash
tag/shared/bin/handoff-append --from slut --to slut --kind blocked \
  --summary "Web container has only the git repo; DB/library unset." \
  --needs "local \$TAGSLUT_DB" --needs "local \$MASTER_LIBRARY" --env web
```

Announce a new versioned identity export for hag to consume:

```bash
tag/shared/bin/handoff-append --from slut --to hag --kind data-release \
  --summary "Published track_identity v4 export." \
  --artifact exports/track_identity.v4.parquet:slut:<sha256>:4
```

## Environment variables the writer understands

- `HANDOFF_SRC` — path to the producing source repo (for git sha/branch). Defaults to `cwd`.
- `HANDOFF_ENV` — `local|web|phone|unknown` override.
- `TAGSLUT_DB`, `MASTER_LIBRARY` — presence is auto-recorded in `resources`.

## Setup in each repo

Add this checkout as a sibling (already at `~/Projects/tag/shared`) or as a
submodule, then paste the boot-block from `AGENT_BOOTBLOCK.md` into each repo's
`AGENT.md`. Step 0 of any resume is `git -C ~/Projects/tag/shared pull` then
`handoff-tail`.
