---
name: read-project-docs-first
description: Read the project's own docs (AGENT.md, docs/law, docs/map, docs/audit, docs/decisions) BEFORE reverse-engineering or modifying a system by grep
metadata:
  type: feedback
---

Read the project's documentation BEFORE reverse-engineering the code or modifying a subsystem. Georges (2026-07-11, sharply): "you dont even read a single project doc." He was right.

**Why:** the tag repo is heavily documented and the docs are BINDING, not background. Grepping the code to reconstruct how intake/compilation/providers work is slower, misses the design intent, and reintroduces bugs the docs already warned about. This is the `resolve-from-the-record` skill applied to *code*, not just decisions — the record includes `docs/`, not only DECISIONS_LOCKED.

**Where to look (slut repo), by topic — read these FIRST when touching the area:**
- **Anything:** `AGENT.md` (canonical instruction file) + `docs/CURRENT.md` / `docs/COMMANDS.md` / `docs/SCRIPT_SURFACE.md`.
- **`docs/law/*`** = ACCEPTED, binding. `MULTI_PROVIDER_ID_POLICY.md` (provider IDs, 5-tier confidence, conflict-flagging), `0004-compilation-evidence-storage-model.md` (compilation evidence = versioned canonical JSON payload + the repair report is a MANDATORY gate artifact with fixed required fields).
- **`docs/map/*`** = system maps: `intake.md`, `compilation-repair.md`, `COMPILATION_LABEL_REPAIR_MANUAL.md`, `COMPILATION_MIGRATION_PROMPT_COOKBOOK.md`.
- **`docs/audit/2026-06-18-intake-to-promotion-script-audit.md`** = the intake→promotion SCRIPT CHAIN map (would have saved the get-intake vs intake.py-stage archaeology).
- **`docs/decisions/*`** = ADRs (0010 analysis boundary, 0011 data-layer invariants, 0012 naming).
- **`docs/v4/2026-07-03-{ts-stage-membership-and-receipt,v4-intake-write-contract}-spec.md`** = the v4 intake contracts (cited in the v3-redirect code).

**How to apply:** when a task touches intake, providers, compilation, membership, naming, or writes — do a `find docs -iname '*<topic>*'` and read the `law/`+`map/`+relevant `decisions/` doc BEFORE writing code. If a doc governs the thing and my design diverges, that's an escalation (per resolve-from-the-record), not a silent choice. See [[beatport-api-gotchas]], [[provider-matching-method]].
