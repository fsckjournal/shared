---
name: feedback_spine-open-is-a-claim-not-a-verdict
description: A spine "open" flag / handoff-tail --open question-text is an INHERITED claim to verify against the ledger+ADRs, not a verdict to relay; reconcile rendered contradictions with judgment
metadata:
  type: feedback
---

A spine `open` status (or the question-text `handoff-tail --open` renders) is an **inherited claim**, held to the same verification bar as a derived one — NOT a settled verdict to echo into a brief.

**Why:** In the first `brief-me` run I relayed "#168 naming form still open" straight from the `--open` renderer. Georges pushed back ("this is the one place I shouldn't have to push back"). Reading the raw #168 text + ADR-0012 showed the TEMPLATE was decided (ADR-0012 ACCEPTED); only the rename ACTION was deferred. The spine renders an open question that an accepted ADR already answers = stale-as-rendered, and catching exactly that is the method (resolve-from-the-record). I ran the method only after he doubted me — backwards.

**How to apply:** Before putting any "open" item in a brief, cross-check it against DECISIONS_LOCKED + the referenced ADR. If a locked decision answers it, it is stale, not open — say so and reconcile the two into ONE clear picture (decided X / deferred Y), don't relay both as if untangling them were the operator's job. Use judgment, don't just relay-and-conflate. A spotted stale-open you don't file is a bug — close it durably (see [[feedback_operator-rulings-not-a-lane]] for the from-whom trap). Resolved this run: #168 closed via #188 (operator-advisor ruling), template=ADR-0012, rename unblocked post-audit.
