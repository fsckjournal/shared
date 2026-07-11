---
name: dont-dismiss-sanctioned-flags
description: Never tell Georges to drop a CLI flag/feature he's deliberately using — check the record first; unknown-flag errors are often unbuilt-but-specced features
metadata:
  type: feedback
---

When a `ts-get`/`ts-stage` flag errors as "unknown option", do NOT advise dropping it or call it a typo. Resolve from the record first (spine, RADICAL_COLLAPSE doc, DECISIONS_LOCKED).

**Why:** On 2026-07-10 Georges ran `ts-get <qobuz album> --listen`; it failed `rc=2`. I told him to drop `--listen`. He corrected me: he asked for it for a reason. `--listen` is his OWN sanctioned membership intake flag (spine #134: enum mix/listen/unclassified, "flag IS the field"; #141: Part 2 = build `--mix`/`--listen` on ts-get+ts-stage, "grep confirms no --mix/--listen exists on the CLI"). The error was an UNBUILT-but-specced feature forwarded to qobuz-dl, not a bad flag. His single-album usage was exactly the mandated album-grain scope.

**How to apply:** An "unknown option" on his tooling is a signal to check whether it's a specced-but-unbuilt feature (grep the spine/decisions for the flag name) BEFORE suggesting removal. Believe his reports (see [[never-delete-masters-verify-his-reports]]); he uses flags for reasons. Build the missing wiring, don't strip the flag.
