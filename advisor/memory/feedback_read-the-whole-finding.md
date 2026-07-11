---
name: read-the-whole-finding
description: Read a finding to its last line before classifying it — the operative conclusion (often a dependency/prerequisite) is frequently the closing sentence; don't dismiss a nuanced result as scope-creep off its headline
metadata:
  type: feedback
---

**Read the WHOLE finding before you classify it. The load-bearing conclusion is often the last line.**

**Why (2026-07-11):** briefing off spine #191/#194, I summarized the MIK no_waveform corruption work as
"weak signal / scope-creep — do NOT fold into v3-kill prereqs" and wrote that into both WEEKLY_PLAN and
the v3_kill prompt. But #194's closing line was the operative one: *"Bridge stays blocked — v3
canonicalization onto a v4 that still prefers stub masters remains unsafe."* The no_waveform **flag**
is weak; the **stub-master finding** is a real blocker-(2) prerequisite. I latched onto the headline
("detector is noisy") and dropped the dependency in the tail. Georges: *"you didn't read the last
part????"* — the same class as this session's earlier misses (relaying the spine instead of reading the
transcript; searching REM instead of `mdfind`-ing the actual `.shortcut` files on disk).

**How to apply:**
- Before filing anything as "noise / weak / scope-creep," read the finding to its END and extract its
  explicit conclusion + any dependency it names. A weak *signal* can still carry a load-bearing
  *consequence* — separate the two claims; don't let the headline verdict swallow the tail.
- A result that names a prerequisite, a blocker, or an "X stays unsafe until Y" clause is NEVER
  scope-creep — that clause IS the actionable core. Elevate it, don't bury it.
- This is [[resolve-from-the-record]] applied to findings, not just decisions: the record includes the
  reasoning's conclusion, not only its top-line number. Related failure shape: [[dont-be-optimistic-prove-identity]]
  (headline optimism over the risk surface) and [[spine-open-is-a-claim-not-a-verdict]] (relay vs.
  reconcile). Concrete instance: [[v3-kill-stub-master-prereq]].
