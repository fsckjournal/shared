---
name: move-dont-menu
description: Georges wants execution and movement, not menus or narration; reserve explicit questions for genuine mutually-exclusive forks that are truly his to decide
metadata:
  type: feedback
---

When working with Georges: **move, don't menu.** Default to executing — query, find the
split, build on a safe copy, show counts — rather than asking what to do next.

**Why:** He is a solo operator, often exhausted, and has been burned repeatedly by agents
that hand back a plan/menu instead of a fix ("stop narrating, run the query, find the
split"). He rejected an `AskUserQuestion` outright when the decision wasn't genuinely his
(the record already answered it). Redundant asking reads as the documented failure mode.

**How to apply:**
- Resolve from the record first; only surface a question when the ledger AND record
  genuinely fail *and* the choice is his to make.
- A genuine mutually-exclusive **architecture fork** IS worth one crisp `AskUserQuestion`
  — he accepted the "console stack" question because the stack choice determined the
  canonical-store consequence. Frame the consequence per option; recommend one.
- Do NOT re-conflate distinct problems. He explicitly separates symptoms of the same
  disease (e.g. the DB split vs the editorial membership split) — solve them separately.
- When he validates a direction ("it works", "this is it"), **stop polishing.** He handles
  visual/UX design himself later (Claude design). Land the record and the backbone; don't
  keep gilding the app.
- For a live defect/build: apply → verify → land on a safe copy. Never leave it as a plan.

See [[resolve-from-the-record]] discipline and the two-store-disease pattern.
