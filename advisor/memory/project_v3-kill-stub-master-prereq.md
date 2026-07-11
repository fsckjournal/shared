---
name: v3-kill-stub-master-prereq
description: The stub/corrupt-preferred-master hazard is a v3-kill blocker-#2 (intake bridge) PREREQUISITE — the append-only bridge must not canonicalize onto a track whose preferred master is a stub/truncated file
metadata:
  type: project
---

**v3-kill is gated on more than the 5 code blockers — there is a DATA prerequisite on blocker (2).**

The append-only content_sha256 bridge (blocker #2, `v4-intake-write-contract-spec.md` §6) canonicalizes
new intake onto v4's **preferred `archive_master` per track**. If that preferred master is a
**corrupt / truncated / 15-second stub** file, the resolver attaches new intake to garbage — so the
bridge is UNSAFE until the preferred master for every track it will touch is verified good.

**The finding vs the flag (the distinction I got wrong once — spine #191/#194):**
- The **MIK `no_waveform` flag is a WEAK corruption signal** — #194 triage over 396 suspects found
  **0 net-new corrupt** beyond #186's existing 64 (238 clean incl. legit >500MB continuous-mix skips,
  154 off-disk/undetermined = the #192/#193 missing-set, not corruption). So the *detector* is noisy.
- BUT the **stub/corrupt-preferred-master HAZARD it surfaced is load-bearing** — it is a real
  prerequisite to the bridge. #191 concrete case: a track whose v4 preferred `archive_master` is a 15s
  stub (Holy Ghost "Say My Name" Revenge instrumental) — canonicalizing onto that would be corruption-by-design.

**How to apply:** gate blocker (2) on the 64-row `slut/output/corrupt_masters_REVIEW.csv` set
(44 corrupt + 20 truncated, #186): for every track the bridge will canonicalize, confirm its preferred
master is not in that set — else re-acquire first, or make the resolver pick the good same-`track_id`
sibling. NEVER delete masters (re-acquire only). Do NOT conflate "the no_waveform detector is weak"
with "the corruption finding is irrelevant to v3-kill" — they are different claims. See
[[v4-intake-bridge-and-membership]] (blocker #2 = the bridge), [[radical-collapse-and-hazards]],
[[never-delete-masters]], and the behavioral lesson [[read-the-whole-finding]].
