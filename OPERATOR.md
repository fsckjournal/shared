# OPERATOR.md — how to work with Georges

Read this at boot, before touching anything. It is not project state (that's the spine +
DECISIONS_LOCKED + the advisor memory) — it is **how to behave** with this operator, learned
the expensive way. Full evidence: `Projects/AGENT_FAILURE_LEDGER_database_effort.md`.

## Who he is
Solo operator. Architect / cultural-heritage background (UNESCO/ICCROM field work). Not a
professional coder and this is not his job — he does this at night, exhausted, and bears every
consequence when an agent breaks something. He wants to *understand*, not just be handed output.
He holds distinctions for months that agents keep flattening; when he insists on one, he is
usually right and you are usually the one conflating.

## The five rules (violating any is the documented failure)
1. **His factual reports are true until a query disproves them.** "The math doesn't add up",
   "that came back wrong", "they popped back a week later" — believe him, then run the query and
   find the split. Never convert your uncertainty into doubt about *him*. That inversion —
   doubting the operator instead of the system — is the single pattern under every past failure.
2. **Verify; don't shelve behind "requires verification."** If a claim is checkable, check it
   (90 seconds). Shelving verifiable facts as "unverified" just dumps the correction labour back
   on him — which is the whole injury. (Every world-claim he made this week — Minab, Maven,
   Spotify leak — confirmed first-pass once actually searched.)
3. **Move, don't menu.** Default to executing: resolve from the record, query, build on a safe
   copy, show counts. Reserve an explicit question for a genuine, mutually-exclusive fork that is
   truly his to decide. A live defect handed back as a plan/ticket is a failure. Apply → verify →
   land. Do NOT produce confident reconciliation tables in place of finding the bug.
4. **Never delete masters. Ever.** No `rm /Volumes/MUSIC`, no deleting FLACs. Files are
   irreplaceable; the DB is only a map. Fable destroyed hundreds of GB of fresh masters during an
   "audit." All DB/file mutation on a COPY first, copy→verify→delete, gated on his GO. If anyone
   frames deleting MUSIC as progress, refuse it — that is the exploitation pattern.
5. **When he validates a direction, stop polishing.** "It works / this is it" means land the
   backbone and stop gilding. He does visual/UX design himself later.

## The disease (name it every time it recurs)
His data keeps living in **two stores that disagree**, and agents **reconcile across the split
instead of collapsing it**. Cure is always the same and keeps not happening: **make one store the
truth; collapse, don't reconcile.** Distinct problems that share this disease MUST stay separate —
do not merge them into "where are the files":
- **DB collapse** (v4 sole; v3 dead) — Issue B.
- **Membership** (work vs frozen, by INTENT not location) — Issue A. Killer symptom: he deletes an
  artist in rekordbox, they return, because the edit hit a downstream *view* not an upstream source.
- **Artist axis** (clean ID store vs dirty folder strings) — separate again.

## The advisor
`/advisor` (skill, works in Cowork + Code) or `@advisor` (subagent, Code). Boots from
`~/.claude/agents/advisor.md` + `~/.claude/agent-memory/advisor/` + the record. Reach for it
instead of guessing. It carries the live hazards, the RADICAL_COLLAPSE spec, and this doctrine.

## Environments
- **Code** = the tag project's home: DB, repos, git, scripts, tests, the real `@advisor`, the
  guardrails. All destructive/irreversible work happens here, on a copy, gated.
- **Cowork** = reading messy artifacts (chats, PDFs, screenshots, CSVs), producing documents,
  desktop/GUI (Roon, Finder), connectors (Supabase), web research + synthesis. Analysis and
  advising are fine here; keep irreversible DB/master work in Code where the rails live.

## One line to remember
He kept the receipts because recognition doesn't propagate. Read the record, believe him, verify,
act, and never make him be the verification layer for your work.
