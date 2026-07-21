# Report: staging evidence and documented Postman resolver run

**Date:** 2026-07-21  
**Scope:** The conversation concerning the 639-file legacy staging root, provider lookup, and whether matched tracks could be promoted.

## Executive summary

No tracks were promoted during this chat. The first provider lookup was run incorrectly against improvised/archived collections and was not reliable evidence. After the documentation was read, the correct YAML Postman collection and exact ISRC-first requests were used with refreshed credentials.

The corrected run submitted 330 unique staging ISRCs. It produced provider evidence for 325 of them:

- Spotify: 252 matched, 28 no-match.
- Beatport: 45 matched, 50 ambiguous, 229 no-match.
- 5 ISRCs had no emitted provider evidence in the logs and remain unaccounted for.

Using the available evidence, 253 rows have at least one provider match. This is a **candidate** count, not an approval-to-promote count. There are 77 rows with no confirmed provider match, including 50 with Beatport ambiguity and 5 with missing provider evidence.

## What happened

1. The initial lookup used an improvised artist/title approach and temporary or archived JSON collections. That was contrary to the repository documentation and did not constitute valid resolver evidence.
2. The concern was raised that the documentation had not been followed.
3. The canonical Postman documentation was read. It identifies:
   - the YAML request directory `postman/collections/tagslut-api/`;
   - the environment `postman/environments/tagslut-env.environment.json`;
   - the documented `tools/postman_tag_resolver.py` seam;
   - ISRC-first provider requests;
   - provider-specific authority rules.
4. `tools/ts-auth all` refreshed the locally managed provider credentials. The Spotify access token was supplied at runtime from the canonical token store; no credential value is recorded here.
5. A dataset of 330 unique ISRCs was built from the active FLAC files in:
   `/Volumes/MUSIC/staging/legacy_discard_restore_20260717`.
   The archived `__satisfied_existing` and `__promoted_verified` areas were excluded.
6. The canonical collection lint passed with zero errors and zero warnings.
7. A one-row smoke test succeeded against Spotify and its documented album-detail follow-up.
8. A single 330-row run reached iteration 186 and then crashed with a Postman CLI JavaScript heap-limit error. This was a runner failure, not evidence of provider failure.
9. The identical documented run was rerun in seven sequential chunks of 50, 50, 50, 50, 50, 50, and 30 rows. The chunk logs are in `/tmp/postman-legacy-search/chunk-logs/`.
10. A legacy `tools/ts-stage --dry-run` was attempted against the mixed staging root to inspect promotion behavior. It reported v3-native registration/scan behavior and stalled after the enrichment step. It was stopped before any further action. It was not used for promotion.

## Evidence artifacts

- Input ISRC dataset: `/tmp/postman-legacy-search/legacy_isrcs.csv`
- Corrected chunk logs: `/tmp/postman-legacy-search/chunk-logs/`
- Candidate list (at least one provider match): `/tmp/postman-legacy-search/promotable-candidates.csv`
- Failed unchunked run log: `/tmp/postman-legacy-search/exact-isrc-run.log`
- Stopped legacy preview: `/tmp/postman-legacy-search/ts-stage-preview.log`

## Interpretation

The 253 matched rows are only provider-resolution candidates. They are not automatically promotable because the documented v4 stage gate also requires:

- release-by-release grouping under a declared release;
- current file hashes and FLAC integrity;
- same-ISRC/different-byte collision checks;
- canonical-library root isolation;
- v4 release membership and occurrence registration;
- a successful receipt and post-promotion database verification.

The staging root is organized as mixed batch folders rather than one declared release. The v4 engine is designed to fail closed on collisions and to process a declared release, so the root must be partitioned into release-scoped batches before execution.

## Current status

**Completed:**

- Correct collection and environment identified.
- Credentials refreshed through the documented auth command.
- 330 unique ISRCs submitted through the canonical ISRC-first requests.
- 253 provider-match candidates identified.
- Candidate CSV written.

**Unresolved:**

- 77 rows have no confirmed provider match or complete evidence.
- 5 rows have no emitted provider evidence and require log/input reconciliation.
- 50 Beatport results are ambiguous and must not be promoted without an unambiguous decision.
- The 253 candidates have not yet passed release grouping, collision, hash, root-isolation, receipt, and live DB gates.

**Not done:**

- No FLAC was moved out of staging.
- No master was overwritten.
- No tag write was performed.
- No promotion or v4 registration was performed in this chat.

## Safe next plan

1. Reconcile the five ISRCs missing provider evidence against the input CSV and chunk logs.
2. Partition the 253 candidates by exact release identity and staging path.
3. Run the documented v4 stage preview per release group, with current hash, membership, collision, and root-isolation output captured.
4. Exclude ambiguous, unmatched, corrupt, duplicate-byte, and collision rows.
5. Execute only release groups whose preview satisfies every gate.
6. Verify each receipt against `music_v4.db`, including occurrence links, file identity, foreign keys, and integrity.
7. Keep unresolved and rejected files in staging with a disposition manifest; do not delete them.

## Bottom line

The corrected lookup established **253 provider-match candidates**, not 253 approved promotions. The correct next action is a release-grouped, receipt-backed v4 preview and gate—not another broad provider search and not a whole-root promotion.
