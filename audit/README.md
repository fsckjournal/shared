# Tag governance auditor — operator runbook

The auditor is the local, independent implementation of the governance design recorded
in spine #309. It supersedes Perplexity operationally while retaining the useful policy
layers. Spine #310 supplies the closed two-store condition it guards, and #312 records
the deployment.

It reads the shared spine, repository hooks, REM freshness, Claude/Codex event logs,
advisor persona, advisor skill, and `resolve-from-the-record` skill. Deterministic checks
establish structural facts; the separate local Qwen layer judges evidence entailment.
Qwen is independent of the cloud agents being audited, not claimed to be unbiased.

## Authority boundary

The auditor is report-only. It may write timestamped reports, private evidence packets,
`latest` files, and `NEEDS_ATTENTION` under:

```text
/Users/g/Library/Logs/tag-governance-audit/
```

It cannot repair findings, append to the spine, update a baseline, edit skills/personas,
write REM, touch a database, or mutate master media. Any repair requires a separate,
explicitly authorized action.

## Run it

Run the complete audit on demand:

```sh
/Users/g/Projects/tag/shared/bin/audit_ledger.py --full
```

Run deterministic checks without the local model:

```sh
/Users/g/Projects/tag/shared/bin/audit_ledger.py --full --no-semantic
```

Limit an investigative run to one or more domains:

```sh
/Users/g/Projects/tag/shared/bin/audit_ledger.py --only ledger --only hooks --no-semantic
```

Available domains are `ledger`, `stores`, `hooks`, `personas`, `events`, `rem`,
`secrets`, and `semantic`. `--recent N` controls how many recent spine entries are sent
to Qwen. Persona/skill content is sent only when its hash differs from the accepted
integrity manifest.

## Weekly schedule

Install or inspect the Monday 08:30 system-local LaunchAgent:

```sh
/Users/g/Projects/tag/shared/bin/install-governance-audit install
/Users/g/Projects/tag/shared/bin/install-governance-audit status
```

The LaunchAgent label is `com.tag.governance-audit`. It runs Monday at 08:30 according
to the Mac's current local timezone. The installed plist lives at
`~/Library/LaunchAgents/com.tag.governance-audit.plist`; the reviewed source is
`audit/com.tag.governance-audit.plist`.

To retire the job without deleting its configuration:

```sh
/Users/g/Projects/tag/shared/bin/install-governance-audit uninstall
```

Uninstall moves the installed plist to a timestamped retired file. Reports are retained
indefinitely in v1.

## Interpret results

Every terminal, Markdown, and JSON result begins with a deterministic executive
conclusion. It states the verdict, whether immediate action is required, established
violation and degraded-check counts, accepted historical-warning count, current advisory
count, and a short `review_recommended` list. Reading this conclusion does not require
Codex, Claude, or another model.

Verdicts are:

- `PASS`: no violations, degraded checks, or warnings.
- `PASS_WITH_HISTORICAL_WARNINGS`: only accepted pre-auditor history remains visible.
- `PASS_WITH_ADVISORIES`: no immediate action; listed current advisories merit review.
- `FAIL`: an established deterministic violation requires action.
- `DEGRADED`: at least one required check could not produce a trustworthy result.

Exit codes are 0 for clean/warning-only, 1 for established violations, and 2 for an
incomplete or degraded audit. `NEEDS_ATTENTION` is confined to the report directory.

- `PASS`: check completed and found no breach.
- `WARN`: accepted history, drift requiring review, or advisory semantic finding.
- `FAIL`: deterministic current violation; exit 1.
- `UNKNOWN`: a required check could not reach a trustworthy result; exit 2.
- `SKIPPED(reason)`: deliberately outside the selected run mode.

Model timeout, malformed JSON, unavailable endpoint, or failed calibration is always
`UNKNOWN`, never `PASS`. Deterministic findings remain in the report even when the
semantic layer is degraded.

The historical ledger cutoff never grandfathers credential exposure. High-confidence
token/key patterns in any ledger line are `SECRET-LEDGER-001` current failures, with only
a SHA-256 fingerprint reported; the matching credential material is never reproduced.

The Markdown report is the operator summary. The JSON report is the machine-readable
record. Exact semantic evidence packets are local files with mode 0600; ordinary reports
contain their path and hash rather than copying private persona content.

## Reviewed configuration

Changes to `baseline.json`, `rules.json`, `hooks_manifest.json`, or
`integrity_manifest.json` require a cited review. A changed advisor, persona, or record
skill is sent to the local semantic judge and remains a warning until its reviewed
manifest is deliberately updated.

- `baseline.json`: accepted historical findings only. Every entry requires an ID, entry
  hash, reason, citation, review date, and `accepted_by` authority.
- `rules.json`: protected targets, destructive verbs, policy exceptions, and the
  pre-auditor ledger cutoff. New findings after the cutoff are not inherited warnings.
- `hooks_manifest.json`: expected file hashes and active `core.hooksPath` configuration.
  All three repos currently execute Shared's tracked `git-safe` hook; old Perplexity
  guard files are present but dormant.
- `integrity_manifest.json`: reviewed advisor/persona/skill hashes and the advisor-memory
  tree digest.

The auditor compares its working bytes with `HEAD:bin/audit_ledger.py`. A mismatch is a
self-integrity warning. Updating a manifest to silence a finding is a governed decision,
not an automatic repair.

## Expected historical warnings

The initial deployment deliberately preserves visibility of:

- historical schema deviations in the append-only ledger;
- duplicate IDs 41, 105, 106, 112, and 113;
- historical artifacts no longer available at their recorded locations;
- backup litter currently adjacent to `handoff.jsonl`.

These warnings do not make a run fail. Novel duplicates, new schema violations, current
missing receipts, hook drift, two-store regression, or deterministic policy violations
do.

## Troubleshooting

- Confirm the model endpoint: `curl http://127.0.0.1:8080/v1/models`.
- Inspect the last report: `open ~/Library/Logs/tag-governance-audit/latest.md`.
- Inspect scheduler state: `bin/install-governance-audit status`.
- Validate the tracked plist: `plutil -lint audit/com.tag.governance-audit.plist`.
- Run deterministic-only to separate model availability from record failures.

The staleness check can detect a missed weekly run only when the auditor next executes;
it is not an independent liveness monitor.

The dated deployment verification receipt is
[`ACCEPTANCE_2026-07-21.md`](ACCEPTANCE_2026-07-21.md).
