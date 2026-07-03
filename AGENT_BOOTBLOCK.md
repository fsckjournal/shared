<!-- Paste this block near the top of BOTH ~/Projects/tag/hag/AGENT.md and
     ~/Projects/tag/slut/AGENT.md. Replace <THIS_REPO> with `hag` or `slut`. -->

## Cross-repo handoff spine (read before doing anything)

This repo coordinates with its sibling through `~/Projects/tag/shared`, an
append-only handoff log. Do **not** hand-write `HANDOFF_*.md` files, paste
free-text handoff summaries, or add `MSG-NNN` blocks to `hag/RELAY.md` — those
channels are **superseded**. `hag/RELAY.md` is frozen at MSG-007 (read it for
history only); `DECISIONS_LOCKED.md` remains the decision ledger but is no
longer hand-mirrored between repos.

**On session start (step 0), always:**

```bash
git -C ~/Projects/tag/shared pull --ff-only
cat ~/Projects/tag/shared/STATE.md          # current truth, both repos — read FIRST
cat ./STATE.md                              # this repo's current truth
~/Projects/tag/shared/bin/handoff-tail --to <THIS_REPO> --open   # only OPEN items
```

`STATE.md` is the reconstructed current state — read it instead of walking the
log. The log answers "what happened, in order"; `STATE.md` answers "what is true
now." Act on anything addressed to `<THIS_REPO>` (or `both`) and resolve open
questions/blocks before starting new work.

**When you finish, UPDATE `STATE.md`** (both this repo's and the shared cross-repo
file) so the next session doesn't have to reconstruct it. Reserve log events
(`handoff-append`) for things the OTHER side must act on — questions, answers,
data-releases, blocks — **not status prose**. Status lives in `STATE.md`.

**When you finish a unit of work, hand it over:**

```bash
HANDOFF_SRC="$PWD" ~/Projects/tag/shared/bin/handoff-append \
  --from <THIS_REPO> --to <OTHER_REPO> --kind handoff \
  --summary "<one paragraph: what changed, what the other repo should do>" \
  [--artifact <repo-relative-path>:<THIS_REPO>[:<sha256>[:<generation>]]] \
  [--open "<unresolved decision>"] \
  [--session <claude-session-id>]
then: git -C ~/Projects/tag/shared add -A && \
      git -C ~/Projects/tag/shared commit -m "handoff: <THIS_REPO>→<OTHER_REPO>" && \
      git -C ~/Projects/tag/shared push
```

**To reply to / resolve an open item**, reference its id and set status —
that clears it from everyone's `--open` list:

```bash
~/Projects/tag/shared/bin/handoff-append --from <THIS_REPO> --to <OTHER_REPO> \
  --kind answer --re <ID> --status answered \
  --summary "<the answer>"
```

**If you cannot proceed because a resource is missing** (e.g. `$TAGSLUT_DB` or
`$MASTER_LIBRARY` isn't mounted in a web/phone session), record it instead of
producing work that can't run:

```bash
~/Projects/tag/shared/bin/handoff-append --from <THIS_REPO> --to <THIS_REPO> \
  --kind blocked --summary "<what you tried>" --needs "<what must exist>"
```

**Rules:** the log is the source of truth (not `state/*.json`, not repo docs);
never edit past log lines; every write goes through `handoff-append`.
