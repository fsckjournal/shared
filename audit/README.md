# Tag governance auditor

The auditor reads the shared spine, repository guardrails, REM freshness, agent event
logs, and the reviewed advisor/record-skill integrity manifest. It writes only to
`~/Library/Logs/tag-governance-audit/`.

Run the complete audit on demand:

```sh
/Users/g/Projects/tag/shared/bin/audit_ledger.py --full
```

Run deterministic checks without the local model:

```sh
/Users/g/Projects/tag/shared/bin/audit_ledger.py --full --no-semantic
```

Install or inspect the Monday 08:30 system-local LaunchAgent:

```sh
/Users/g/Projects/tag/shared/bin/install-governance-audit install
/Users/g/Projects/tag/shared/bin/install-governance-audit status
```

Exit codes are 0 for clean/warning-only, 1 for established violations, and 2 for an
incomplete or degraded audit. `NEEDS_ATTENTION` is confined to the report directory.
The auditor never repairs a finding or appends to the spine.

Changes to `baseline.json`, `rules.json`, `hooks_manifest.json`, or
`integrity_manifest.json` require a cited review. A changed advisor, persona, or record
skill is sent to the local semantic judge and remains a warning until its reviewed
manifest is deliberately updated.
