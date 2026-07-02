<!-- Paste this block near the top of BOTH ~/Projects/tag/hag/AGENT.md and
     ~/Projects/tag/slut/AGENT.md. Replace <THIS_REPO> with `hag` or `slut`. -->

## Cross-repo handoff spine (read before doing anything)

This repo coordinates with its sibling through `~/Projects/tag/shared`, an
append-only handoff log. Do **not** hand-write `HANDOFF_*.md` files or paste
free-text handoff summaries between sessions — that channel is deprecated.

**On session start (step 0), always:**

```bash
git -C ~/Projects/tag/shared pull --ff-only
~/Projects/tag/shared/bin/handoff-tail --to <THIS_REPO> --open
```

Act on anything addressed to `<THIS_REPO>` (or `both`) and resolve open
questions/blocks before starting new work.

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

**If you cannot proceed because a resource is missing** (e.g. `$TAGSLUT_DB` or
`$MASTER_LIBRARY` isn't mounted in a web/phone session), record it instead of
producing work that can't run:

```bash
~/Projects/tag/shared/bin/handoff-append --from <THIS_REPO> --to <THIS_REPO> \
  --kind blocked --summary "<what you tried>" --needs "<what must exist>"
```

**Rules:** the log is the source of truth (not `state/*.json`, not repo docs);
never edit past log lines; every write goes through `handoff-append`.
