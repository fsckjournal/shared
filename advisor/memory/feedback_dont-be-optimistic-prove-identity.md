---
name: dont-be-optimistic-prove-identity
description: Georges flags optimistic framing; don't conflate quality-superiority (or any fuzzy match) with identity — prove same-recording before treating dupes as safe
metadata:
  type: feedback
---

When I summarized 407 dupeGuru sha-disagree groups as "overwhelmingly benign and mechanical,"
Georges pushed back: **"I think you're being a bit too optimistic."** He was right — my
`quality_ladder` tag only proved one file had a higher *spec*, not that the two were the same
recording. Under a real identity gate (ISRC / duration / fingerprint), only 212/407 were
confirmed same-recording; 195 held, of which 132 had **disagreeing ISRCs = different recordings**
dupeGuru had merely fuzzy-matched.

**Rule:** Do not present reassuring/optimistic conclusions to Georges — he wants the skeptical read.
And NEVER conflate "better quality" or "grouped together by a tool" with "same thing." A dedupe/merge
tool's grouping (dupeGuru, acoustic match, tag match) is a FLAG, never identity proof.

**Why:** This is the Fable-shape risk in miniature — a confident reconciliation that would have
swapped/deleted across genuinely different recordings. Georges has been burned by agents narrating
false confidence over unverified identity; he catches it and calls it out.

**How to apply:** Before any replace/merge/dedupe treats two items as the same, require a POSITIVE
identity signal (ISRC match, acoustic fingerprint, content hash) — and when the signal is missing,
tag it HOLD/ambiguous, don't assume. When reporting, lead with what is NOT confirmed and the size of
the risk surface, not the happy-path count. See [[never-delete-masters-verify-his-reports]] (verify
direction differs: believe HIS reports, doubt MY optimistic inferences) and [[move-dont-menu]].
Locked outcome: DECISIONS_LOCKED §11(e) replace-and-inherit, gated on confirmed same-recording.
