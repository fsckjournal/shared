---
name: resolve-from-the-record
description: # Resolve from the record

## Why this exists
Resolve from the record
Why this exists
Teams (and their agents) waste enormous effort re-deciding things that were already
decided — often with less rigor than the original call, and sometimes silently
reversing a hard-won agreement because a newer session didn't know it existed. The
antidote is cheap: most answers already live in the project's record. Consult it
before spending your own reasoning, an advisor's turn, or the operator's attention.
Your reasoning time is not the bottleneck — rediscovery is. A 30-second query beats
a 30-minute re-derivation, and it beats re-litigating a decision that was settled on
evidence you didn't see.
The three places answers live
Before doing anything, locate these in the project (they have different names in
different repos — find the local equivalents):

The ledger — the authoritative, current decisions. Look for
DECISIONS_LOCKED.md, docs/decisions/, ADRs (adr-*.md), a "Decisions" section
in a README, or a pinned issue. This is what's true now.
The record — the historical reasoning: past chat/session transcripts, a memory
store, prior PRs, an audit log. This is how we got here and why, and it may hold
resolutions that never reached the ledger. Usually it's a searchable tool, not a folder
to skim: a memory-query CLI over past sessions, a full-text index over agent transcripts,
git log/git blame. Search every history surface you have, not just the first one —
different agents and tools keep separate records (e.g. one index of your Claude sessions,
another of a different agent's history), and the resolution may live in the one you didn't
check. The concrete commands for a given project (the exact CLI, its path) belong in that
project's AGENT.md/onboarding, not in this skill — but if such a tool exists, it is your
first stop, ahead of your own reasoning.
The channel — the append-only coordination surface where open questions and
answers are routed: a handoff log/spine, an issue tracker, a CHANGELOG, a decisions
inbox. This is where you escalate things that aren't resolved.

If a project has none of these, say so and degrade gracefully (see "When the record is
thin"). Don't invent authority that isn't there.
The protocol — do these in order
When you face a question that feels previously-decided, or you're about to re-derive a
design choice, reverse a prior call, or escalate to a human/advisor:

Every claim gets the same verification bar — including the ones you didn't derive.
A statement handed to you by the prompt, the ledger, or the record is not pre-verified.
Apply the steps below to inherited claims exactly as you would to your own — especially
before you promote one into a deliverable others will treat as fact (a spec, a count, an
exclusion). Rigor applied only to claims you generate yourself is selective rigor, and
selective rigor is how a scoping aside becomes a wrong "population of 17,707." The tell is
often numeric: two figures that nearly match, an assumption quietly hardening into a number.


Check the ledger. If it answers the question, follow it and cite the exact
section. A locked decision is not yours to revisit without a fresh agreement among
whoever owns it. Stop here — you're done.
Search the record for the reasoning, or for anything the ledger doesn't cover.
Use whatever search the project provides (a memory-query CLI, full-text over
transcripts, git log/git blame, grep over docs). Read the actual source, not a
summary — the why usually matters more than the what.
If the record holds a resolution the ledger is missing → apply it, cite the
source (transcript#turn, commit SHA, doc line), and propose adding it to the
ledger so the next person doesn't re-derive it. Closing this gap is the whole game.
If sources contradict (two different resolutions, or the record vs. the ledger)
→ do NOT silently pick the newer/louder one, and do NOT just mention it in
your reply — that buries it. Escalate it to the channel as a routed, open item
that persists until a human resolves it. Make it durable and findable: state both
positions with their dates and provenance, and what decision is needed. Escalating a
spotted contradiction is mandatory; a contradiction you noticed but didn't file is a
bug.
Advisor / human = last resort. Consult one only after the ledger and the record
genuinely fail to resolve it — and when you do, open with what you already checked
("ledger has no entry; searched the record for X, found only stale context"), so they
start where the record left off instead of from zero.
Always cite your source (LEDGER §X, transcript#turn, commit, doc line). An
answer without a citation is a re-derivation, not a resolution — and it can't be
audited or trusted later.

Escalation, concretely
The point of escalation is that a contradiction becomes a durable, routed, still-open
item — not a line in one agent's transcript that scrolls away. Use the project's
append-only channel. In a handoff-spine style setup that means appending an open
question addressed to the relevant owners; in a GitHub-style setup it means opening an
issue (labeled, assigned) rather than a comment; in a doc-based setup it means a dated
entry in a "Needs decision" list that boot/onboarding reads.
Minimum content of a good escalation:

What contradicts — position A (source + date) vs position B (source + date).
Why it matters — what breaks or drifts if it's left unresolved.
What's needed — the specific decision and who owns it.

Then it stays open until answered. When it's answered, record the resolution in the
ledger, and close the item.
When the record is thin
If the project has no ledger, no searchable history, and no channel, this skill still
helps as a stance: prefer git log/git blame/existing docs over re-deriving; when you
must decide without a record, write the decision down (start the ledger — an
ADR/DECISIONS.md entry) so it becomes part of the record for next time; and when you
escalate to the human, do it durably (an issue, a tracked note), not just in chat.
Leaving a trail is how a thin record becomes a useful one.
What good looks like (worked example)
A fresh session sees a claim: "Library X is obsolete, replaced by Y." Instead of acting
on it:

Ledger says "Library X is the chosen approach" (older entry). Conflict noticed.
Record (searched) surfaces the deep, evidence-based discussion that adopted X,
and a later session that declared it obsolete — but the later one never weighed the
original's evidence.
Because these contradict, the agent does not silently switch. It escalates:
files an open item — "LEDGER §X (adopt X) vs 2026-07-03 session (X obsolete, replaced
by Y); the original was evidence-based, the reversal wasn't; needs a fresh decision" —
and reads the code to gather facts for whoever resolves it.
The resolution, once made, updates the ledger and closes the item. The next agent
who wonders reads the ledger, sees it's settled, and moves on.

Zero re-derivation, zero silent reversal, one durable escalation. That's the loop.
"Resolved from the record" is not "problem solved"
Finding the answer in the record is where a question ends — but only where a live defect
begins. If the task is an error, a crash, a failing build, or anything currently broken, the
record gives you the sanctioned fix pattern, not the finish line. A live failure is itself
proof that the settled decision isn't implemented on this path yet — very often it was
applied to one code path and you're standing in a second, uncovered one.
So split the two cases before you declare victory:

The task was a question ("what did we decide about X", "which approach do we use") →
finding it in the record, cited, is the resolution. Stop.
The task is a defect (something is failing right now) → resolving from the record means:
(a) identify the sanctioned decision/fix, (b) apply it to the failing path, (c) verify
the failure is actually gone. Diagnosis is step one, not the deliverable. Don't hand back
"the record explains this, here's the plan" and stop — that leaves the operator to notice it's
still broken and push you to finish. Cross from knowing to doing on your own.

When it's a defect that the record already decided but didn't implement here, that's a gap,
not a contradiction — no escalation needed; close the gap by porting the sanctioned fix, then
verify. (Reserve escalation for genuine disagreements between sources, per the protocol above.)
Make your resolution auditable — so a human doesn't have to re-verify it
The goal is not that you never err; it's that your errors are cheap to catch. A reviewer
should be able to audit a page, not re-derive your work. When a deliverable (a spec, a count,
a decision) will be treated as ground truth by others, three habits make it verifiable at a
glance instead of on faith:

Ship receipts. Every load-bearing claim carries the exact command/query that produced it,
inline or in an appendix — reproducible by paste-and-run, not "trust me." An uncited number
is then a red flag a reviewer can spot without re-doing the analysis.
Label verified vs. assumed. Mark each claim [verified: <query>] or
[assumed: from prompt/record — UNVERIFIED]. This shrinks the human's job to reviewing the
short assumed list — the actual risk surface — instead of the whole document. The most
dangerous claim is an assumption wearing the clothes of a fact; labeling strips the disguise.
Run a verification pass on the load-bearing numbers. Before "done," independently
re-derive the figures that decisions hinge on — a fresh pass, or a second agent — and
reconcile any mismatch. Catch it yourself so the operator doesn't have to catch it for you.
If you're the operator building this into a workflow: don't gate sign-off on the whole
document, gate it on the decisions + the assumed-list. That's a review a human can actually do.

Before you WRITE to the record — don't re-encode a settled decision
Everything above is read-side: consult the record before you decide. But the same
discipline binds the moment you write to it — adding or editing a ledger entry, an ADR, a
spec others will treat as truth. Most silent drift enters here, not at read time. The
mechanism: an agent restates an already-governing decision in fresh vocabulary; the
restatement drifts from the original's axis; now two "authoritative" entries quietly
disagree, and the next reader inherits the fork. (This is how a measured-vs-provider
ownership rule got re-locked as a list of tool names and drifted — a closed box, reopened by
paraphrase.)

Find the governing decision first. Before locking a new entry, search the record for a
decision that already governs the same question (an older lock, an ADR, a settled thread).
If one exists, your entry implements it — cite it, and use its vocabulary and its
axis. Don't paraphrase it into new terms.
A vocabulary shift is a drift smell. If the record frames a decision along one axis
(e.g. provenance: measured vs provider) and you catch yourself re-expressing it along
another (e.g. tool names), stop — you're not recording the decision, you're forking it.
Translate only with the mapping cited inline.
Re-encoding ≠ recording. Restating a settled decision in your own words, without citing
the source it descends from, is not a record — it's a second source of truth waiting to
disagree with the first. Cite-and-stay-faithful, or don't write it.

Operator approval is not verification — and is never a defense
The record is the source of truth. The operator's "yes" is not. A human approving your
framing is a fallible signal given under limited attention — it ratifies the intent of a
decision; it does not certify that your wording faithfully encodes the record. Two directions,
both mandatory:

Never launder your own drift through approval. "Operator-approved" on an entry does not
make its wording correct. If you wrote it, you still own its fidelity to the governing
record, and you verify it against the source — approval does not discharge that bar.
Never use approval against the person, or cite it as why a claim is right. "But you
approved it" is not evidence and not a defense. The operator is allowed to be wrong under
load; keeping the record honest is your job, not theirs. Treat their approval as trust to
protect, never a receipt to invoke back at them.

Anti-patterns to avoid

Re-deriving a decision the ledger already records. Read first.
Reversing by recency. A newer statement doesn't outrank a locked, reasoned one —
surface the conflict, don't resolve it by timestamp.
Silent tie-breaking. Picking a side of a contradiction without escalating hides a
real disagreement and guarantees it recurs.
Escalating to a human first. That's the expensive path; exhaust the record first
and arrive with what you already found.
Uncited answers. If you can't point to where the answer lives, treat it as unresolved.
Trusting inherited claims. A number or category from the prompt, ledger, or record is not
pre-verified — promote it into a deliverable only after you'd stake a query on it. The failure
is quiet: you apply real rigor to everything except the one claim you never thought to doubt.
Re-encoding a settled decision in new vocabulary. Cite the governing entry and stay
faithful to its axis, or don't write. A restatement that drifts forks the truth.
Citing operator approval as verification. Approval ratifies intent; it never certifies
fidelity to the record, and it is never a defense to invoke back at the person.
---
