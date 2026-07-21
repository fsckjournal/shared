#!/usr/bin/env python3
"""Read-only governance audit for the tag agent ecosystem."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_DIR = Path.home() / "Library/Logs/tag-governance-audit"
DEFAULT_MODEL = "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit"
DEFAULT_BASE_URL = "http://127.0.0.1:8080/v1"
ALLOWED_FIELDS = {
    "schema_version", "id", "re", "status", "ts", "from", "to", "kind",
    "summary", "git", "env", "resources", "open_questions", "needs",
    "artifacts", "session",
}
REQUIRED_FIELDS = {"schema_version", "id", "status", "ts", "from", "to", "kind", "summary"}
ENUMS = {
    "from": {"hag", "slut"},
    "to": {"hag", "slut", "both"},
    "kind": {"handoff", "blocked", "question", "answer", "data-release", "note"},
    "status": {"open", "answered", "fyi"},
    "env": {"local", "web", "phone", "unknown"},
}


@dataclass
class Finding:
    check_id: str
    status: str
    severity: str
    summary: str
    evidence: dict[str, Any]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_digest(path: Path) -> str:
    h = hashlib.sha256()
    for child in sorted(path.rglob("*.md")):
        h.update(str(child.relative_to(path)).encode())
        h.update(b"\0")
        h.update(sha256_file(child).encode())
        h.update(b"\n")
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def run_capture(args: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        result = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=30, check=False)
        return result.returncode, result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)


class Auditor:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.findings: list[Finding] = []
        self.entries: list[dict[str, Any]] = []
        self.raw_entries: list[bytes] = []
        self.changed_semantic_files: list[Path] = []
        self.started = dt.datetime.now(dt.timezone.utc)
        self.report_dir = Path(args.report_dir).expanduser()
        self.config_dir = ROOT / "audit"

    def add(self, check_id: str, status: str, summary: str, **evidence: Any) -> None:
        severity = {"PASS": "info", "WARN": "warning", "FAIL": "error",
                    "UNKNOWN": "degraded", "SKIPPED": "info"}[status]
        self.findings.append(Finding(check_id, status, severity, summary, evidence))

    def wants(self, domain: str) -> bool:
        return not self.args.only or domain in self.args.only

    def check_config(self) -> None:
        try:
            baseline = load_json(self.config_dir / "baseline.json")
            required = {"finding_id", "entry_hash", "reason", "source_citation",
                        "review_date", "accepted_by"}
            rows = baseline.get("accepted_findings")
            if not isinstance(rows, list):
                raise ValueError("accepted_findings must be a list")
            for index, row in enumerate(rows):
                if not isinstance(row, dict) or required - row.keys():
                    missing = sorted(required - set(row if isinstance(row, dict) else {}))
                    raise ValueError(f"baseline row {index} missing {missing}")
                if not re.fullmatch(r"[0-9a-f]{64}", str(row["entry_hash"])):
                    raise ValueError(f"baseline row {index} has invalid entry_hash")
            self.baseline_hashes = {row["entry_hash"] for row in rows}
            load_json(self.config_dir / "rules.json")
            load_json(self.config_dir / "hooks_manifest.json")
            load_json(self.config_dir / "integrity_manifest.json")
            self.add("CONFIG-001", "PASS", "Audit configuration is structurally valid",
                     accepted_findings=len(rows))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self.baseline_hashes = set()
            self.add("CONFIG-001", "FAIL", "Audit configuration is invalid", error=str(exc))

    def check_ledger(self) -> None:
        path = ROOT / "handoffs/handoff.jsonl"
        try:
            data = path.read_bytes()
        except OSError as exc:
            self.add("LEDGER-001", "FAIL", "Ledger cannot be read", error=str(exc))
            return
        if data and not data.endswith(b"\n"):
            self.add("LEDGER-002", "FAIL", "Ledger lacks a final newline", path=str(path))
        bad = 0
        for lineno, raw in enumerate(data.splitlines(), 1):
            if not raw.strip():
                continue
            try:
                entry = json.loads(raw)
                if not isinstance(entry, dict):
                    raise ValueError("entry is not an object")
                entry["_audit_line"] = lineno
                self.entries.append(entry)
                self.raw_entries.append(raw)
            except (json.JSONDecodeError, ValueError) as exc:
                bad += 1
                self.add("LEDGER-001", "FAIL", "Malformed ledger entry",
                         line=lineno, error=str(exc))
        if not bad:
            self.add("LEDGER-001", "PASS", "Every non-empty ledger line is valid JSON",
                     entries=len(self.entries))

        rules = load_json(self.config_dir / "rules.json")
        historical_cutoff = int(rules.get("historical_ledger_cutoff_line", 0))
        ids: defaultdict[int, list[tuple[int, str]]] = defaultdict(list)
        known_ids = set()
        previous_ts: dt.datetime | None = None
        for entry, raw in zip(self.entries, self.raw_entries):
            line = entry["_audit_line"]
            clean = {k: v for k, v in entry.items() if not k.startswith("_audit_")}
            missing = REQUIRED_FIELDS - clean.keys()
            extra = clean.keys() - ALLOWED_FIELDS
            errors: list[str] = []
            if missing:
                errors.append(f"missing={sorted(missing)}")
            if extra:
                errors.append(f"unexpected={sorted(extra)}")
            if clean.get("schema_version") != 1:
                errors.append("schema_version must equal 1")
            if not isinstance(clean.get("id"), int) or clean.get("id", 0) < 1:
                errors.append("id must be a positive integer")
            for field, allowed in ENUMS.items():
                if field in clean and clean[field] not in allowed:
                    errors.append(f"{field} has invalid value")
            summary = clean.get("summary")
            if not isinstance(summary, str) or not 1 <= len(summary) <= 2000:
                errors.append("summary length must be 1..2000")
            if clean.get("kind") == "blocked" and not clean.get("needs"):
                errors.append("blocked entry requires non-empty needs")
            if "re" in clean and (not isinstance(clean["re"], int) or clean["re"] < 1):
                errors.append("re must be a positive integer")
            for artifact in clean.get("artifacts", []) or []:
                if not isinstance(artifact, dict) or "path" not in artifact:
                    errors.append("artifact requires path")
                elif "sha256" in artifact and not re.fullmatch(r"[0-9a-f]{64}", str(artifact["sha256"])):
                    errors.append("artifact sha256 is invalid")
            if errors:
                status = "WARN" if line <= historical_cutoff else "FAIL"
                self.add("LEDGER-003", status,
                         "Historical ledger schema deviation" if status == "WARN" else "Ledger schema violation",
                         line=line, errors=errors, historical_cutoff=historical_cutoff)
            if isinstance(clean.get("id"), int):
                known_ids.add(clean["id"])
                ids[clean["id"]].append((line, sha256_bytes(raw)))
            try:
                parsed_ts = dt.datetime.fromisoformat(str(clean.get("ts", "")).replace("Z", "+00:00"))
                if previous_ts and parsed_ts < previous_ts - dt.timedelta(minutes=10):
                    self.add("LEDGER-005", "WARN", "Timestamp moved backwards beyond tolerance",
                             line=line, timestamp=clean.get("ts"),
                             historical=line <= historical_cutoff)
                previous_ts = parsed_ts
            except ValueError:
                status = "WARN" if line <= historical_cutoff else "FAIL"
                self.add("LEDGER-003", status, "Invalid ISO-8601 timestamp", line=line)

        for entry in self.entries:
            if "re" in entry and entry["re"] not in known_ids:
                status = "WARN" if entry["_audit_line"] <= historical_cutoff else "FAIL"
                self.add("LEDGER-004", status, "Reply references a missing ledger ID",
                         line=entry["_audit_line"], referenced_id=entry["re"],
                         historical=status == "WARN")
        duplicates = {key: rows for key, rows in ids.items() if len(rows) > 1}
        for entry_id, rows in duplicates.items():
            hashes = {value for _, value in rows}
            if hashes <= self.baseline_hashes:
                self.add("LEDGER-006", "WARN", "Accepted historical duplicate ID",
                         entry_id=entry_id, lines=[line for line, _ in rows])
            else:
                self.add("LEDGER-006", "FAIL", "Novel or changed duplicate ID",
                         entry_id=entry_id, lines=[line for line, _ in rows], hashes=sorted(hashes))
        if not duplicates:
            self.add("LEDGER-006", "PASS", "Ledger IDs are unique")
        if not any(f.check_id == "LEDGER-003" for f in self.findings):
            self.add("LEDGER-003", "PASS", "Ledger entries satisfy the local schema subset")

        self.check_ledger_policy(historical_cutoff)
        litter = sorted(str(p) for pattern in ("handoff.jsonl.bak_*", "handoff.jsonl.tmp")
                        for p in (ROOT / "handoffs").glob(pattern))
        self.add("LEDGER-008", "WARN" if litter else "PASS",
                 "Backup litter exists beside the append-only ledger" if litter else "No backup litter beside ledger",
                 paths=litter)

    def check_ledger_policy(self, historical_cutoff: int) -> None:
        rules = load_json(self.config_dir / "rules.json")
        verbs = "|".join(re.escape(v) for v in rules["destructive_verbs"])
        targets = "|".join(re.escape(v) for v in rules["protected_paths"])
        destructive = re.compile(rf"(?is)\b(?:{verbs})\b.{{0,120}}(?:{targets})|(?:{targets}).{{0,120}}\b(?:{verbs})\b")
        completion = re.compile(r"(?i)\b(?:fixed|completed|resolved|deployed|landed|verified)\b")
        ledger_secret = re.compile(
            r"(?ix)(?:\b(?:sk-[a-z0-9_-]{16,}|ghp_[a-z0-9]{20,}|github_pat_[a-z0-9_]{20,}|"
            r"xox[baprs]-[a-z0-9-]{16,}|AKIA[A-Z0-9]{16}|eyJ[a-z0-9_-]{10,}\.[a-z0-9_-]{10,}\.[a-z0-9_-]{10,})\b|"
            r"\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|password)\b\s*[:=]\s*['\"]?[a-z0-9_./+=-]{16,})"
        )
        for entry in self.entries:
            summary = str(entry.get("summary", ""))
            line = entry["_audit_line"]
            secret_match = ledger_secret.search(summary)
            if secret_match:
                matched = secret_match.group(0)
                digest = sha256_bytes(matched.encode())
                self.add("SECRET-LEDGER-001", "FAIL",
                         "Potential live credential material appears in ledger history",
                         line=line, entry_id=entry.get("id"),
                         fingerprint=f"{digest[:4]}...{digest[-4:]}",
                         historical_cutoff_ignored=True)
            if destructive.search(summary):
                status = "WARN" if line <= historical_cutoff else "FAIL"
                self.add("POLICY-001", status,
                         "Historical protected-target operation reference" if status == "WARN" else "Destructive operation references a protected target",
                         line=line, entry_id=entry.get("id"), historical=status == "WARN")
            direct_write = re.search(
                r"(?i)\b(?:hag|gemini|we|i)\b.{0,40}\b(?:wrote|updated|inserted|deleted|dropped|mutated)\b.{0,80}\bmusic_v4(?:\.db)?\b",
                summary,
            )
            if entry.get("from") == "hag" and direct_write:
                status = "WARN" if line <= historical_cutoff else "FAIL"
                self.add("LANE-001", status,
                         "Historical Hag direct-v4 mutation claim" if status == "WARN" else "Hag claims a direct v4 mutation",
                         line=line, entry_id=entry.get("id"), citation="decisions/DECISIONS_LOCKED.md section 5")
            if completion.search(summary) and entry.get("artifacts"):
                for artifact in entry["artifacts"]:
                    path = self.resolve_artifact(artifact)
                    if path and not path.exists():
                        status = "WARN" if line <= historical_cutoff else "FAIL"
                        self.add("CLAIM-001", status,
                                 "Historical completion claim cites an unavailable artifact" if status == "WARN" else "Completion claim cites a missing artifact",
                                 line=line, entry_id=entry.get("id"), path=str(path))

    @staticmethod
    def resolve_artifact(artifact: dict[str, Any]) -> Path | None:
        value = artifact.get("path")
        if not isinstance(value, str) or not value:
            return None
        candidate = Path(value).expanduser()
        if candidate.is_absolute():
            return candidate
        tag_root = ROOT.parent
        parts = candidate.parts
        if parts and parts[0] in {"shared", "slut", "hag", "slut_db"}:
            return tag_root / candidate
        roots = {"shared": ROOT, "slut": tag_root / "slut", "hag": tag_root / "hag"}
        return roots.get(artifact.get("repo", "shared"), ROOT) / candidate

    def check_two_store(self) -> None:
        live = Path("/Users/g/Projects/shared")
        retired = Path("/Users/g/Projects/_retired/shared_stale_20260713_20260721")
        if live.exists():
            self.add("STORE-001", "FAIL", "Retired duplicate shared spine has reappeared",
                     path=str(live), citation="handoff.jsonl id=310")
        else:
            self.add("STORE-001", "PASS", "Resolved duplicate shared spine remains absent",
                     citation="handoff.jsonl id=310")
        if retired.exists():
            self.add("STORE-002", "PASS", "Preserved retired clone remains available", path=str(retired))
        else:
            self.add("STORE-002", "WARN", "Expected retired clone is absent; verify deliberate re-archive",
                     path=str(retired), citation="handoff.jsonl id=310")

    def check_hooks(self) -> None:
        try:
            manifest = load_json(self.config_dir / "hooks_manifest.json")
            for row in manifest.get("repo_hooks_path", []):
                code, actual = run_capture(["git", "config", "--get", "core.hooksPath"],
                                           cwd=Path(row["repo_path"]))
                expected = row["expected"]
                self.add("HOOK-000", "PASS" if code == 0 and actual == expected else "FAIL",
                         "Repository uses the reviewed active hook path" if code == 0 and actual == expected else "Repository active hook path drifted",
                         repo=row["repo"], expected=expected, actual=actual if code == 0 else None)
            for row in manifest.get("hooks", []):
                path = Path(row["path"])
                if not path.exists():
                    self.add("HOOK-001", "FAIL", "Expected hook is missing", path=str(path), role=row.get("role"))
                    continue
                actual = sha256_file(path)
                self.add("HOOK-001", "PASS" if actual == row["sha256"] else "FAIL",
                         "Hook matches reviewed manifest" if actual == row["sha256"] else "Hook drifted from reviewed manifest",
                         path=str(path), role=row.get("role"), expected=row["sha256"], actual=actual)
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            self.add("HOOK-001", "FAIL", "Hook manifest cannot be evaluated", error=str(exc))

    def check_integrity(self) -> None:
        try:
            manifest = load_json(self.config_dir / "integrity_manifest.json")
            for row in manifest.get("files", []):
                path = Path(row["path"])
                if not path.exists():
                    self.add("PERSONA-001", "FAIL", "Governance file is missing", path=str(path), role=row.get("role"))
                    continue
                actual = sha256_file(path)
                changed = actual != row["sha256"]
                self.add("PERSONA-001", "WARN" if changed else "PASS",
                         "Governance file changed and requires semantic review" if changed else "Governance file matches accepted manifest",
                         path=str(path), role=row.get("role"), expected=row["sha256"], actual=actual)
                if changed and row.get("semantic_review"):
                    self.changed_semantic_files.append(path)
            for row in manifest.get("trees", []):
                path = Path(row["path"])
                if not path.is_dir():
                    self.add("PERSONA-002", "FAIL", "Governance tree is missing", path=str(path))
                    continue
                actual = tree_digest(path)
                self.add("PERSONA-002", "WARN" if actual != row["sha256"] else "PASS",
                         "Governance tree changed" if actual != row["sha256"] else "Governance tree matches accepted manifest",
                         path=str(path), expected=row["sha256"], actual=actual)
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            self.add("PERSONA-001", "FAIL", "Integrity manifest cannot be evaluated", error=str(exc))

    def check_jsonl_tail(self, check_id: str, path: Path, label: str) -> None:
        if not path.exists():
            self.add(check_id, "FAIL", f"{label} is missing", path=str(path))
            return
        malformed = 0
        lines = path.read_bytes().splitlines()[-200:]
        for raw in lines:
            try:
                json.loads(raw)
            except json.JSONDecodeError:
                malformed += 1
        age = self.started.timestamp() - path.stat().st_mtime
        status = "FAIL" if malformed else ("WARN" if age > 8 * 86400 else "PASS")
        summary = f"{label} has malformed recent records" if malformed else (
            f"{label} is stale" if age > 8 * 86400 else f"{label} is readable and recent")
        self.add(check_id, status, summary, path=str(path), sampled=len(lines), malformed=malformed,
                 age_hours=round(age / 3600, 1))

    def check_events(self) -> None:
        self.check_jsonl_tail("EVENT-CLAUDE-001", Path.home() / ".claude/grounding-gate/events.jsonl", "Claude grounding events")
        self.check_jsonl_tail("EVENT-CODEX-001", Path.home() / ".codex/grounding-gate/events.jsonl", "Codex grounding events")
        settings = Path.home() / ".claude/settings.json"
        if settings.exists():
            try:
                data = json.loads(settings.read_text())
                text = json.dumps(data)
                active = "grounding" in text.lower()
                self.add("EVENT-CLAUDE-002", "PASS" if active else "WARN",
                         "Claude settings reference grounding hooks" if active else "Claude settings do not visibly reference grounding hooks",
                         path=str(settings))
            except json.JSONDecodeError as exc:
                self.add("EVENT-CLAUDE-002", "FAIL", "Claude settings JSON is malformed", error=str(exc))
        else:
            self.add("EVENT-CLAUDE-002", "FAIL", "Claude settings are missing", path=str(settings))

    def check_rem(self) -> None:
        root = Path.home() / "Projects/rem"
        manifest = root / "capture_manifest.jsonl"
        self.check_jsonl_tail("REM-001", manifest, "REM capture manifest")
        masters = root / "masters"
        self.add("REM-002", "PASS" if masters.is_dir() else "FAIL",
                 "REM masters directory is available" if masters.is_dir() else "REM masters directory is missing",
                 path=str(masters))
        code, output = run_capture([str(root / "bin/rem"), "status"], cwd=root)
        self.add("REM-003", "PASS" if code == 0 else "WARN",
                 "REM status command succeeded" if code == 0 else "REM status command unavailable",
                 exit_code=code, output=output[-2000:])
        verify_code, verify_output = run_capture(
            [sys.executable, str(root / "bin/rem_capture.py"), "verify"], cwd=root
        )
        verify_summary = verify_output.splitlines()[-1] if verify_output else "no output"
        self.add(
            "REM-004", "PASS" if verify_code == 0 else "WARN",
            "REM captured-master hashes match their manifest" if verify_code == 0
            else "REM captured-master integrity has unresolved mismatches",
            exit_code=verify_code, summary=verify_summary,
        )
        self.check_rem_privacy(root)

    def check_rem_privacy(
        self,
        root: Path,
        cold_store: Path = Path("/Users/g/Projects/_retired/rem_chatgpt_masters_20260721"),
    ) -> None:
        records = root / "normalized/records.jsonl"
        config_path = root / "config/sensitivity.json"
        classifier_path = root / "bin/sensitivity_filter.py"
        failures: Counter[str] = Counter()
        samples = 0
        sample_hits = 0
        sample_fingerprints: list[str] = []
        try:
            config = load_json(config_path)
            default_private = {
                surface for surface, visibility in config.get("surface_defaults", {}).items()
                if visibility == "private"
            }
            spec = importlib.util.spec_from_file_location("rem_sensitivity_audit", classifier_path)
            if not spec or not spec.loader:
                raise ValueError("cannot load sensitivity classifier")
            classifier = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(classifier)
            classifier_sha = sha256_file(classifier_path)
            with records.open(encoding="utf-8", errors="replace") as handle:
                for raw in handle:
                    try:
                        row = json.loads(raw)
                    except json.JSONDecodeError:
                        failures["malformed_record"] += 1
                        continue
                    visibility = row.get("visibility")
                    if visibility not in {"indexed", "private", "review"}:
                        failures["missing_or_invalid_visibility"] += 1
                    if visibility != "indexed":
                        continue
                    if row.get("surface") in default_private:
                        failures["default_private_surface_indexed"] += 1
                    if row.get("sensitivity_categories"):
                        failures["categorized_record_indexed"] += 1
                    # Deterministic spread across the file without loading the corpus.
                    record_id = str(row.get("id", ""))
                    if samples < 200 and record_id and int(sha256_bytes(record_id.encode())[:4], 16) % 97 == 0:
                        samples += 1
                        categories = classifier.tier1_categories(
                            str(row.get("title", "")), str(row.get("text", ""))
                        )
                        if categories:
                            sample_hits += 1
                            sample_fingerprints.append(sha256_bytes(record_id.encode())[:12])
            code, tracked = run_capture(["git", "ls-files", "private", "quarantine"], cwd=root)
            if code != 0:
                failures["git_tracking_check_unavailable"] += 1
            elif tracked.strip():
                failures["sensitive_tier_tracked"] += len(tracked.splitlines())
            if (root / "masters/chatgpt").exists():
                failures["chatgpt_master_source_reappeared"] += 1
            if not cold_store.exists():
                failures["chatgpt_cold_store_missing"] += 1
            if not (root / "private").is_dir():
                failures["private_tier_missing"] += 1
            if sample_hits:
                failures["tier1_hit_in_indexed_sample"] += sample_hits
            self.add(
                "REM-PRIV-001", "FAIL" if failures else "PASS",
                "REM privacy boundary violated" if failures else "REM privacy boundary is enforced",
                failures=dict(failures), sampled_indexed_records=samples,
                sample_hit_fingerprints=sample_fingerprints,
                classifier_sha256=classifier_sha,
            )
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            self.add("REM-PRIV-001", "UNKNOWN", "REM privacy boundary could not be audited",
                     error=str(exc))

    def check_secrets(self) -> None:
        pattern = re.compile(
            r"os\.getenv\(\s*(['\"])([A-Z0-9_]*(?:SECRET|TOKEN|API_KEY|APP_ID|CLIENT_ID))\1\s*,\s*(['\"])([^'\"]{12,})\3\s*\)"
        )
        exceptions = load_json(self.config_dir / "rules.json").get("policy_exceptions", [])
        except_paths = {row.get("path") for row in exceptions}
        hits = 0
        for repo in (ROOT, ROOT.parent / "slut", ROOT.parent / "hag"):
            code, output = run_capture(["git", "ls-files", "-z"], cwd=repo)
            if code:
                self.add("SECRET-001", "UNKNOWN", "Could not enumerate tracked files", repo=str(repo), error=output)
                continue
            for name in output.split("\0"):
                if not name:
                    continue
                path = repo / name
                if (str(path) in except_paths or not path.is_file()
                        or path.suffix not in {".py", ".sh"} or path.stat().st_size > 2_000_000):
                    continue
                try:
                    text = path.read_text(errors="ignore")
                except OSError:
                    continue
                for match in pattern.finditer(text):
                    value = match.group(4)
                    digest = sha256_bytes(value.encode())
                    line = text.count("\n", 0, match.start()) + 1
                    self.add("SECRET-001", "FAIL", "Literal credential fallback in tracked source",
                             path=str(path), line=line, fingerprint=f"{digest[:4]}...{digest[-4:]}")
                    hits += 1
        if not hits and not any(f.check_id == "SECRET-001" and f.status == "UNKNOWN" for f in self.findings):
            self.add("SECRET-001", "PASS", "No literal getenv credential fallbacks found in tracked source")

    def self_trust(self) -> dict[str, Any]:
        path = Path(__file__).resolve()
        working = sha256_file(path)
        try:
            result = subprocess.run(["git", "show", "HEAD:bin/audit_ledger.py"], cwd=ROOT,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    timeout=30, check=False)
            committed = sha256_bytes(result.stdout) if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            committed = None
        status = "PASS" if committed == working else "WARN"
        self.add("SELF-001", status,
                 "Auditor matches committed Git blob" if status == "PASS" else "Auditor is uncommitted or differs from committed Git blob",
                 working_sha256=working, committed_sha256=committed)
        code, head = run_capture(["git", "rev-parse", "HEAD"], cwd=ROOT)
        return {"path": str(path), "working_sha256": working, "committed_sha256": committed,
                "matches_committed": committed == working, "repo_head": head if code == 0 else None}

    def semantic_packet(self) -> dict[str, Any]:
        recent = []
        for entry in self.entries[-self.args.recent:]:
            recent.append({k: v for k, v in entry.items() if not k.startswith("_audit_")})
        changed = []
        for path in self.changed_semantic_files:
            content = path.read_text(errors="replace")
            changed.append({"path": str(path), "sha256": sha256_file(path), "content": content[:12000]})
        rules = load_json(self.config_dir / "rules.json")["semantic_change_review"]
        return {"recent_ledger_entries": recent, "changed_governance_files": changed,
                "review_principles": rules["principles"]}

    def semantic(self) -> dict[str, Any] | None:
        if self.args.no_semantic or self.args.quick:
            self.add("SEMANTIC-001", "SKIPPED", "Semantic review disabled for this run")
            return None
        packet = self.semantic_packet()
        prompt = (
            "You are an independent, evidence-first auditor. Do not assume a claim is true merely "
            "because it is in a ledger. Review the evidence packet for unsupported inference, material "
            "omission, lane violations, and weakening of changed governance skills/personas. "
            "Review every ledger entry independently. The audit covers all tag governance domains; "
            "adjacent entries are not one task and a change of topic is never a finding. "
            "A blocked/open alert reports an unresolved condition and does not require a resolution, "
            "rollback, or completion receipt. Do not flag it merely because remediation is pending. "
            "Reporting or quoting a prohibited action is not itself a lane violation; require an explicit "
            "claim that the emitting agent performed the prohibited action. Do not invent a primary focus. "
            "Every finding must identify the exact entry/file and a concrete contradiction or missing evidence. "
            "Goal drift cannot be judged without an explicit assignment in the packet; none is supplied here. "
            "Calibration: a completion claim with a missing required receipt is FAIL; a blocked alert without "
            "a resolution receipt is PASS; two independent topics are PASS; reporting somebody else's lane "
            "violation is PASS for the reporter. Return strict JSON only with keys calibration (object with "
            "completion_without_receipt='FAIL', blocked_alert_without_resolution_receipt='PASS', "
            "independent_topics='PASS', reported_violation_is_performed_violation='PASS'), status "
            "(PASS|WARN|FAIL|UNKNOWN), findings (array of objects with category, reasoning, evidence; "
            "evidence must be an array of exact entry IDs or file paths).\n"
            + json.dumps(packet, ensure_ascii=False)
        )
        prompt_hash = sha256_bytes(prompt.encode())
        evidence = {"model": self.args.model, "prompt_sha256": prompt_hash, "packet": packet}
        self.report_dir.mkdir(parents=True, exist_ok=True)
        evidence_path = self.report_dir / f"evidence-{self.started.strftime('%Y%m%dT%H%M%SZ')}.json"
        self.secure_write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")
        body = json.dumps({"model": self.args.model, "messages": [{"role": "user", "content": prompt}],
                           "temperature": 0, "max_tokens": 1400}).encode()
        request = urllib.request.Request(self.args.base_url.rstrip("/") + "/chat/completions",
                                         data=body, headers={"Content-Type": "application/json",
                                                             "Authorization": "Bearer not-needed"})
        try:
            with urllib.request.urlopen(request, timeout=self.args.timeout) as response:
                payload = json.load(response)
            raw = payload["choices"][0]["message"]["content"].strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.S)
            result = json.loads(raw)
            calibration = result.get("calibration", {})
            expected_calibration = {
                "completion_without_receipt": "FAIL",
                "blocked_alert_without_resolution_receipt": "PASS",
                "independent_topics": "PASS",
                "reported_violation_is_performed_violation": "PASS",
            }
            if any(calibration.get(key) != value for key, value in expected_calibration.items()):
                raise ValueError("calibration response failed required controls")
            status = result.get("status")
            if status not in {"PASS", "WARN", "FAIL", "UNKNOWN"} or not isinstance(result.get("findings"), list):
                raise ValueError("semantic response has invalid schema")
            for finding in result["findings"]:
                if (not isinstance(finding, dict) or not isinstance(finding.get("category"), str)
                        or not isinstance(finding.get("reasoning"), str)
                        or not isinstance(finding.get("evidence"), list)):
                    raise ValueError("semantic finding has invalid schema")
                reasoning = finding["reasoning"].lower()
                if "separate topic" in reasoning or "primary focus" in reasoning:
                    raise ValueError("semantic finding contradicts independent-topic calibration")
            self.add("SEMANTIC-001", status, "Independent semantic review completed",
                     model=self.args.model, prompt_sha256=prompt_hash, evidence_packet=str(evidence_path),
                     findings=result["findings"])
            return result
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as exc:
            self.add("SEMANTIC-001", "UNKNOWN", "Semantic review unavailable or invalid",
                     model=self.args.model, prompt_sha256=prompt_hash, evidence_packet=str(evidence_path), error=str(exc))
            return None

    @staticmethod
    def secure_write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(content)
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def previous_success_age(self) -> float | None:
        path = self.report_dir / "last_successful_run"
        try:
            stamp = dt.datetime.fromisoformat(path.read_text().strip().replace("Z", "+00:00"))
            return (self.started - stamp).total_seconds() / 86400
        except (OSError, ValueError):
            return None

    def build_conclusion(self, statuses: Counter[str]) -> dict[str, Any]:
        warnings = [finding for finding in self.findings if finding.status == "WARN"]

        def accepted_history(finding: Finding) -> bool:
            return (
                bool(finding.evidence.get("historical"))
                or finding.summary.startswith("Historical ")
                or finding.summary.startswith("Accepted historical ")
                or (
                    finding.check_id == "LEDGER-003"
                    and isinstance(finding.evidence.get("line"), int)
                    and finding.evidence["line"] <= int(finding.evidence.get("historical_cutoff", 0))
                )
            )

        historical = [finding for finding in warnings if accepted_history(finding)]
        current = [finding for finding in warnings if not accepted_history(finding)]
        if statuses["FAIL"]:
            verdict = "FAIL"
            summary = f"{statuses['FAIL']} established violation(s); immediate action required."
        elif statuses["UNKNOWN"]:
            verdict = "DEGRADED"
            summary = f"{statuses['UNKNOWN']} check(s) could not reach a trustworthy result; review required."
        elif current:
            verdict = "PASS_WITH_ADVISORIES"
            summary = (
                f"No established violations or degraded checks. No immediate action required; "
                f"review {len(current)} current advisory item(s) when convenient."
            )
        elif historical:
            verdict = "PASS_WITH_HISTORICAL_WARNINGS"
            summary = "No established violations, degraded checks, or current advisories."
        else:
            verdict = "PASS"
            summary = "No established violations, degraded checks, or advisory findings."
        return {
            "verdict": verdict,
            "immediate_action_required": bool(statuses["FAIL"] or statuses["UNKNOWN"]),
            "summary": summary,
            "established_violations": statuses["FAIL"],
            "degraded_checks": statuses["UNKNOWN"],
            "accepted_historical_warnings": len(historical),
            "current_advisories": len(current),
            "review_recommended": [
                {"check_id": finding.check_id, "summary": finding.summary}
                for finding in current
            ],
        }

    def execute(self) -> tuple[int, dict[str, Any]]:
        self.check_config()
        if self.wants("ledger"):
            self.check_ledger()
        if self.wants("stores"):
            self.check_two_store()
        if self.wants("hooks"):
            self.check_hooks()
        if self.wants("personas"):
            self.check_integrity()
        if not self.args.quick and self.wants("events"):
            self.check_events()
        if not self.args.quick and self.wants("rem"):
            self.check_rem()
        if not self.args.quick and self.wants("secrets"):
            self.check_secrets()
        trust = self.self_trust()
        age = self.previous_success_age()
        if age is not None and age > 8:
            self.add("SCHEDULE-001", "WARN", "Last successful audit is older than eight days", age_days=round(age, 1))
        else:
            self.add("SCHEDULE-001", "PASS", "No observable audit-staleness breach",
                     age_days=round(age, 1) if age is not None else None,
                     limitation="Only evaluated when the auditor runs")
        semantic = self.semantic() if self.wants("semantic") else None
        statuses = Counter(f.status for f in self.findings)
        exit_code = 1 if statuses["FAIL"] else (2 if statuses["UNKNOWN"] else 0)
        conclusion = self.build_conclusion(statuses)
        finished = dt.datetime.now(dt.timezone.utc)
        report = {
            "schema_version": 1,
            "started_at": self.started.isoformat().replace("+00:00", "Z"),
            "finished_at": finished.isoformat().replace("+00:00", "Z"),
            "duration_seconds": round((finished - self.started).total_seconds(), 3),
            "mode": "quick" if self.args.quick else "full",
            "semantic": "disabled" if self.args.no_semantic or self.args.quick else (semantic or "degraded"),
            "auditor": trust,
            "status_counts": dict(statuses),
            "conclusion": conclusion,
            "exit_code": exit_code,
            "findings": [asdict(f) for f in self.findings],
        }
        return exit_code, report

    def write_report(self, report: dict[str, Any]) -> tuple[Path, Path]:
        stamp = self.started.strftime("%Y%m%dT%H%M%SZ")
        json_path = self.report_dir / f"audit-{stamp}.json"
        md_path = self.report_dir / f"audit-{stamp}.md"
        self.secure_write(json_path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        conclusion = report["conclusion"]
        lines = ["# Tag Governance Audit", "", "## Executive conclusion", "",
                 f"**{conclusion['verdict']}** — {conclusion['summary']}", "",
                 f"- Immediate action required: `{'yes' if conclusion['immediate_action_required'] else 'no'}`",
                 f"- Established violations: `{conclusion['established_violations']}`",
                 f"- Degraded checks: `{conclusion['degraded_checks']}`",
                 f"- Accepted historical warnings: `{conclusion['accepted_historical_warnings']}`",
                 f"- Current advisories: `{conclusion['current_advisories']}`", ""]
        for item in conclusion["review_recommended"]:
            lines.append(f"- Review when convenient: **{item['check_id']}** — {item['summary']}")
        lines.extend(["", "## Run metadata", "", f"- Started: `{report['started_at']}`",
                 f"- Exit code: `{report['exit_code']}`", f"- Mode: `{report['mode']}`",
                 f"- Auditor: `{report['auditor']['working_sha256']}`", "", "## Findings", ""])
        for item in report["findings"]:
            lines.append(f"- **{item['status']} {item['check_id']}** — {item['summary']}")
            if item["evidence"]:
                safe = json.dumps(item["evidence"], ensure_ascii=False, sort_keys=True)
                lines.append(f"  - Evidence: `{safe}`")
        self.secure_write(md_path, "\n".join(lines) + "\n")
        self.secure_write(self.report_dir / "latest.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        self.secure_write(self.report_dir / "latest.md", "\n".join(lines) + "\n")
        if report["exit_code"] == 0:
            self.secure_write(self.report_dir / "last_successful_run", report["finished_at"] + "\n")
            marker = self.report_dir / "NEEDS_ATTENTION"
            if marker.exists():
                marker.unlink()
        else:
            self.secure_write(self.report_dir / "NEEDS_ATTENTION",
                              f"exit={report['exit_code']} report={md_path}\n")
        return md_path, json_path


def notify(report_path: Path, exit_code: int) -> None:
    message = f"Tag governance audit needs attention (exit {exit_code}). {report_path}"
    script = f'display notification {json.dumps(message)} with title "Tag governance audit"'
    subprocess.run(["/usr/bin/osascript", "-e", script], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Run deterministic core checks only")
    mode.add_argument("--full", action="store_true", help="Run the full audit (default)")
    parser.add_argument("--only", action="append", choices=["ledger", "stores", "hooks", "personas", "events", "rem", "secrets", "semantic"])
    parser.add_argument("--recent", type=int, default=12, help="Recent ledger entries sent to semantic review")
    parser.add_argument("--model", default=os.environ.get("TAG_AUDIT_MODEL", DEFAULT_MODEL))
    parser.add_argument("--base-url", default=os.environ.get("TAG_AUDIT_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--no-semantic", action="store_true")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    parser.add_argument("--notify", action="store_true", help="Post a macOS notification on exit 1/2")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.recent < 1:
        raise SystemExit("--recent must be positive")
    auditor = Auditor(args)
    exit_code, report = auditor.execute()
    md_path, json_path = auditor.write_report(report)
    print(json.dumps({"conclusion": report["conclusion"], "exit_code": exit_code,
                      "markdown_report": str(md_path), "json_report": str(json_path),
                      "status_counts": report["status_counts"]}, indent=2))
    if args.notify and exit_code:
        notify(md_path, exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
