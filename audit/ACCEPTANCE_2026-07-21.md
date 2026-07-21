# Governance auditor acceptance receipt — 2026-07-21

This receipt closes the two deployment qualifications raised after the first successful
run. It records what was actually executed; it is not a claim that every future run will
remain healthy.

## Historical-warning and secret review

The 40 accepted historical warnings were enumerated from
`audit-20260721T112429Z.json`:

- 14 `CLAIM-001` unavailable historical artifacts;
- 14 `LEDGER-003` historical schema deviations;
- 1 `LEDGER-004` historical missing reply reference;
- 2 `LEDGER-005` historical timestamp-order deviations;
- 5 `LEDGER-006` accepted duplicate IDs;
- 4 `POLICY-001` historical protected-target references.

No `SECRET` warning was grandfathered; the working-tree `SECRET-001` check was `PASS`.
The audit was then hardened so high-confidence credential material in any ledger line is
`SECRET-LEDGER-001: FAIL` regardless of `historical_ledger_cutoff_line`. Findings expose
only a SHA-256 fingerprint. The fixture placing a GitHub-style token before the cutoff
passed and confirmed the raw token was absent from output.

## Failure-path tests

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests/test_audit_ledger.py`
ran 10 tests successfully, including:

- unreachable semantic endpoint → `UNKNOWN`;
- invalid semantic calibration → `UNKNOWN`;
- malformed ledger and novel duplicate → `FAIL`;
- historical credential exposure → current redacted `FAIL`;
- forced exit 1 → `NEEDS_ATTENTION` marker;
- exit-1 notification path → `/usr/bin/osascript` invocation.

A real, non-failure test notification was also submitted to macOS; `osascript` exited 0.

## Live non-mutation check

Hashes were captured, a full deterministic audit was run, and the same hashes were
captured again. Every comparison was `UNCHANGED`:

| Target | SHA-256 before and after |
| --- | --- |
| `handoffs/handoff.jsonl` | `d02eeb4cb36f5d7e6b9d9f76debdf6b56a0dabd4d430bf3447ae57bea55b6f13` |
| REM `capture_manifest.jsonl` | `779f19d7b9523136dba533a63a39cdf308c198e29a412656cd4c8886a6f0f597` |
| canonical `music_v4.db` | `e5028bd15093fe3a2cd4e981dbbf335c705cfda19288608d6329f07e6cc16052` |
| deterministic five-master sample | `5842f4d3d92afff53030e22c4ed48c3d70f2c3a9c8ee0838823c8123419fa1a5` |
| repository status | `0fce935cf25c8f9b0b9c2307d951762e16f217d8081b81bf8ffe6d886013d48d` |

The master receipt is explicitly a deterministic five-file sample, not a claim that the
entire master library was re-hashed during this acceptance run. The auditor has no master
write path.
