# Independent Agent-Governance Auditor — Plan v3

*Revised 2026-07-21 (v3) after operator blocking corrections, each re-verified against the
live record where checkable. Evidence labels: `[verified: …]` = checked against source;
`[assumed]` = design judgment; `[unverified]` = stated but not yet confirmed.*

## Summary

Build a local, **read-only** auditor in `/Users/g/Projects/tag/shared` that checks agent
event logging, ledger use, REM capture, advisor/record skills, personas, and repository
guardrails.

It runs:

* Weekly, every Monday at 08:30 (launchd `StartCalendarInterval`; note this follows the
  Mac's **current system timezone** — "08:30 Asia/Beirut" holds only while the system
  timezone remains Beirut).
* On demand through one documented command.

It does **not** run on every commit.

**Relationship to spine #309 — SUPERSEDES operationally.** #309 (2026-07-21) approved a
Perplexity agent as external, non-executing auditor with a five-layer guardrail design
`[verified: handoff.jsonl id=309]`. That approval was followed by Perplexity permission
failures; the operator's standing instruction is "use the better option." This local
auditor **replaces Perplexity as the implementation mechanism** and **inherits the useful
five-layer design** (the pre-action gate's protected-path policy becomes the retrospective
destructive-op check; this weekly/on-demand auditor does not inherit pre-action timing; record-consistency,
secrets sentinel, two-store detector, contradiction router all map to registered checks
below). The deployment spine entry preserves #309 as history, cites it, and states this
supersession explicitly — one governance surface, not a fork.

## Implementation

### Core

* **Replace, don't refactor,** the untracked `shared/bin/audit_ledger.py` prototype.
  Verified defects `[verified: read of file]`: fail-**open** (JSON-parse failure of the
  model response returns `{"status": "pass"}`), non-stdlib `openai` dependency, and a
  markdown-mangled `base_url` that can never connect — the semantic layer has plausibly
  never produced a real verdict. The rewrite is a correction, not an upgrade.
* Standard-library-only CLI supporting `--quick`, `--full`, `--recent`, `--model`,
  `--only <domain>`, `--no-semantic`, and output options.
* **Check-registry architecture.** Each check registered with a stable ID
  (e.g. `LEDGER-003`, `REM-002`, `HOOK-001`), severity, and skip flag. Reports list
  per-check status including `SKIPPED(<reason>)`.

### Layer split — deterministic vs semantic

Two layers with distinct epistemics; neither is mislabeled as the other:

* **Deterministic (authoritative):** structural and resolvable facts only — JSONL
  validity, schema (`schema/handoff.schema.json`), reference resolution, timestamps,
  duplicate IDs, artifact existence, authority-boundary violations against locked lanes,
  secrets patterns, destructive-operation references. For completion claims, the
  deterministic layer establishes only that **required evidence is present, resolvable,
  and structurally consistent** (receipts exist, cited artifacts exist, no contradiction
  with a locked lane).
* **Semantic (advisory, independent):** whether the evidence actually **entails** the
  claim — unsupported inference, omission, goal drift. This is inherently judgment;
  it lives in Layer 2 and can never override or upgrade a deterministic result.

### Deterministic checks

* **Baseline is a tracked data file**, `audit/baseline.json`, holding **historical
  findings only** — seeded with the verified duplicate-ID set `{41, 105, 106, 112, 113}`
  (each ×2 across 316 entries, 0 malformed) `[verified: json parse of handoff.jsonl]`.
  Baseline findings → WARN; novel → FAIL.
* **Baseline entries are auditable:** every entry requires finding ID, entry hash,
  reason, source citation, review date, and `accepted_by` identifying the operator or
  governing locked decision. A baseline modification without all fields
  is itself a FAIL — otherwise an agent could resolve its own finding by silently
  baselining it.
* **Policy exceptions live separately** in a reviewed rule configuration (e.g.
  `audit/rules.json`), distinct from the historical baseline. Example:
  `tools/_tiddl_auth.py::DEFAULT_AUTH` (third-party tiddl credentials, documented in
  ledger §22) is a sanctioned rule exception, not a historical finding.
* **Ordering/timestamp violations are WARN, not FAIL** (skew tolerance window) —
  multi-session, multi-machine spine `[assumed]`.
* **Secrets check encodes ledger §22** `[verified: DECISIONS_LOCKED.md §22]`: flag
  `os.getenv(key, "<literal>")` credential fallbacks and provider secrets outside
  `~/.config/tagslut/tokens.json`; findings cite §22. **Findings never reproduce a
  detected value** — report rule ID, repo, file, line, and a redacted fingerprint
  (e.g. first/last 4 chars of the SHA-256 of the match) only.
* **Spine-hygiene check:** backup litter staged/untracked next to the append-only
  source of truth (`handoff.jsonl.bak_*`, `.tmp`) is a WARN-class finding.

### Domains audited

* Claude and Codex event-log validity, freshness, and REM coverage.
* REM status, source freshness, quarantine state, search availability. REM path is
  `~/Projects/rem` (relocated 2026-07-10; captures fresh `[verified: manifest tail]`).
* Advisor and `resolve-from-the-record` skill/persona presence, hashes, and mirror
  equality. **Two-store check verifies a RESOLVED condition stays closed** per spine
  #310 `[verified: id=310]`: `/Users/g/Projects/shared` must **not** exist (it was the
  stale clone, frozen at `e7ccbb5`, retired to
  `/Users/g/Projects/_retired/shared_stale_20260713_20260721`, preserved not deleted).
  Reappearance of `/Users/g/Projects/shared`, or disappearance of the retired copy,
  is a FAIL citing #310.
* **Hook auditing compares each repo against an explicit expected manifest**
  (`audit/hooks_manifest.json`), NOT byte-equality across repos. Current verified state
  `[verified: sha256 this session]`: shared's tracked `githooks/pre-commit`
  (`ef01d3f3…`, git-safe enforcement) differs by design from the installed shared hook
  (`0ddabf0e…`, Perplexity-guard variant), which matches the installed and tracked hooks
  in both slut and hag `[verified: sha256 this session]`. All three repositories currently
  set `core.hooksPath` to shared's tracked `githooks`, so the Perplexity-guard files are
  dormant; the manifest audits active hook configuration separately from dormant files.
  Simple equality would produce misleading findings; the manifest records
  (repo → expected hook hash + role), and drift from the manifest is the finding.
* Any check touching v3-era DB state respects known `music_v3.db` corruption:
  path-query counts marked `UNTRUSTED(v3 corruption)` or avoided. v4 is sole canonical
  per ledger §15 (#189/#190).

### Semantic layer

* **Runs weekly by default.** The point of this auditor is independent examination of
  agent conduct and reasoning; without Layer 2 the scheduled run is mostly a schema
  checker. If the model endpoint is unavailable, the run **completes deterministic
  checks normally** and emits a clearly **degraded semantic section**
  (`SEMANTIC: UNAVAILABLE(<reason>)`) with exit 2 — deterministic results are never
  discarded. On-demand runs may pass `--no-semantic`.
* **Independent, not unbiased.** Qwen is not bias-free; its independence claim is that
  it is an open-weights model separate from the agents being audited. Every report
  exposes: model identity, prompt version (hash), calibration outcome, and the exact
  evidence packet sent — so the judge's judgments are themselves auditable.
* Local Qwen (existing 2.5 Coder 14B endpoint) for bounded review of recent entries and
  changed advisor/record-skill/persona files since the accepted integrity manifest.
  Ordinary reports contain paths, hashes, and redacted findings; the exact local evidence
  packet is stored mode 0600 beside the report so private persona content is not copied
  into the Markdown summary.
  Deterministic failures can never be overridden.
* Findings: `PASS`/`WARN`/`FAIL`/`UNKNOWN` with evidence. Timeouts, malformed output,
  failed calibration, unavailable endpoint → `UNKNOWN`, exit 2 — never a pass.
* Calibrate against known valid and known unsupported entries; disable semantic
  verdicts (→ degraded section) if calibration fails.

### Authority & self-trust

* Never modify the ledger, REM, repositories, databases, master media, skills, or
  personas. Reports may include a suggested `handoff-append` command; the auditor
  cannot execute it.
* Every report records the auditor's working-tree SHA-256, the committed Git-blob SHA-256,
  their comparison, and repo HEAD. A current hash alone is not treated as tamper evidence.

## Operation

* On-demand entry point: `shared/bin/audit_ledger.py --full`
* Tracked LaunchAgent template + installer, Mondays 08:30 (system-local time; see
  timezone note above). `StartCalendarInterval` fires on wake if asleep at 08:30,
  skipped if powered off.
* Exit codes: 0 clean/advisory-only, 1 established violations, 2 degraded/incomplete
  (including semantic-unavailable).
* **Surfacing channel.** launchd ignores exit codes; on exit 1 or 2 the run posts a
  macOS notification (`osascript`) and writes a `NEEDS_ATTENTION` marker **inside the
  auditor's own log directory**. No claim of advisor/`brief-me` integration — that
  integration does not exist in the boot path today and would be a separately built
  and tested change.
* **Staleness self-check — with its stated limit:** the auditor records
  last-successful-run and flags `> 8 days` as WARN. This can only report a missed
  interval **on the next invocation** (scheduled or on-demand); it cannot alert while
  the auditor is not running. It is a detection aid, not a liveness guarantee.
* **Reports are kept indefinitely in v1.** No automatic pruning — deletion conflicts
  with the preserve-first posture and weakens the audit trail. An explicit retention
  policy may be added later, reviewed, only if storage becomes material.
* Record scheduler status, duration, model identity (or degraded reason), checked
  evidence, skipped checks, and report locations in every run. Reports under
  `/Users/g/Library/Logs/tag-governance-audit/` (timestamped MD + JSON + `latest`
  pointers).
* **Pre-deployment dirty-tree check is dynamic:** before committing, run
  `git status --porcelain`, enumerate the unrelated dirty work at that moment, and
  commit only the auditor, tests, docs, baseline/rules/manifest, and scheduler files
  with `git-safe commit -m <msg> <explicit paths>` — never bulk, never a hardcoded
  snapshot of today's tree state.
* **Commit environment:** the durable rule is explicit-path `git-safe` commits.
  Check writability of the repo at deployment time from wherever deployment runs;
  if committing from a sandbox/mount proves restricted, run the commit in a Mac
  terminal. (One prior session observed unlink restrictions through a mount; treat
  as environment-specific, verify at deployment, not architecture.)
* After deployment, append one normal spine entry via `handoff-append` documenting:
  report-only authority, weekly + on-demand cadence, evidence paths, and the
  **supersedes-#309-operationally** ruling (Perplexity design inherited, Perplexity
  execution retired; #309 preserved as history).

## Test and Acceptance Plan

* Fixture-test malformed ledger records, missing fields, invalid references, baseline
  vs novel duplicates (fixtures use real IDs 41/105/106/112/113 as baseline cases),
  incomplete baseline entries (missing reason/citation/review-date/accepted-by → FAIL), authority
  violations, structurally-unsupported completion claims (missing receipt / missing
  artifact / locked-lane contradiction), §22-pattern secrets including the
  `os.getenv(key, "literal")` form — asserting the finding output contains **no
  secret material**, only the redacted fingerprint — and benign vs destructive
  protected-path references.
* Test missing skills, persona drift, two-store regression (recreate
  `/Users/g/Projects/shared` in a fixture → FAIL citing #310), stale REM capture,
  corrupt event logs, and hook drift against the manifest (including the
  legitimate tracked-vs-installed difference NOT firing).
* Mock valid, malformed, incomplete, timed-out, and unreachable semantic responses;
  verify no failure path becomes `PASS` and deterministic results survive semantic
  unavailability — regression tests against the prototype's verified fail-open bug.
* Calibrate semantic review; verify calibration failure produces a degraded section,
  not silent PASSes.
* Validate the LaunchAgent with `plutil`; run on-demand; exercise the scheduled
  command manually; verify notification + `NEEDS_ATTENTION` marker on a forced
  exit-1 run.
* Confirm reports generate while repo status, ledger content, REM databases,
  `music_v4.db`, and master-file hashes remain byte-identical (hash before/after).

## Assumptions

* `/Users/g/Projects/tag/shared` is the canonical spine `[verified]`; the two-store
  question is CLOSED per #310 and the auditor guards the closure.
* Existing local Qwen 2.5 Coder 14B server for the semantic layer; no model download.
* Persona content stays private; auditor records integrity metadata, not persona text.
* Repairs identified by an audit require separate explicit authorization.
* v4 is the sole canonical DB (ledger §15); v3 counts untrusted pending recovery.
