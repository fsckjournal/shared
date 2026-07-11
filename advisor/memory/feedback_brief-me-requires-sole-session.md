---
name: feedback_brief-me-requires-sole-session
description: brief-me / any record-read brief must run with NO other sessions active — a live spine moves the snapshot stale mid-brief; Georges quiesces sessions before invoking
metadata:
  type: feedback
---

`brief-me` (and any brief that reads the moving record) is a **point-in-time snapshot**. If other Code/Cowork sessions write the spine while the brief runs, the read is stale before it ships.

**Why:** During the first `brief-me` run the spine advanced from #186 → #188 mid-conversation; #187 (Beatport residual sweep, +327 refs) landed after my snapshot, so the brief's "17,548 Beatport refs" was already one sweep stale when quoted. Georges: "I'll make sure no other sessions are running when I invoke this skill. this should be a rule."

**How to apply:** RULE — brief-me is invoked as the SOLE active session; Georges quiesces others first. If the advisor detects the spine head moved between boot-read and brief-ship (git sha / max handoff id changed), FLAG it explicitly and re-read the affected numbers rather than quoting the stale snapshot. Never present a moving-record figure as current without noting the read timestamp when concurrency is possible.
