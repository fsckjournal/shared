import argparse
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "bin/audit_ledger.py"
SPEC = importlib.util.spec_from_file_location("audit_ledger", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


def args(report_dir, **overrides):
    values = dict(quick=False, full=True, only=None, recent=2,
                  model="test-model", base_url="http://127.0.0.1:1/v1",
                  timeout=0.01, no_semantic=True, report_dir=str(report_dir), notify=False)
    values.update(overrides)
    return argparse.Namespace(**values)


class AuditorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "audit").mkdir()
        (self.root / "handoffs").mkdir()
        self.original_root = audit.ROOT
        audit.ROOT = self.root

    def tearDown(self):
        audit.ROOT = self.original_root
        self.temp.cleanup()

    def write_configs(self, baseline=None):
        (self.root / "audit/baseline.json").write_text(json.dumps({
            "schema_version": 1, "accepted_findings": baseline or []}))
        (self.root / "audit/rules.json").write_text(json.dumps({
            "schema_version": 1, "protected_paths": ["MASTER_LIBRARY"],
            "destructive_verbs": ["rm"], "policy_exceptions": [],
            "semantic_change_review": {"principles": ["keep evidence"]}}))
        (self.root / "audit/hooks_manifest.json").write_text('{"schema_version":1,"hooks":[]}')
        (self.root / "audit/integrity_manifest.json").write_text(
            '{"schema_version":1,"files":[],"trees":[]}')

    def entry(self, entry_id=1, summary="bounded note"):
        return {"schema_version": 1, "id": entry_id, "ts": "2026-07-21T00:00:00Z",
                "from": "slut", "to": "both", "kind": "note", "status": "fyi",
                "summary": summary}

    def test_incomplete_baseline_is_failure(self):
        self.write_configs([{"finding_id": "x"}])
        runner = audit.Auditor(args(self.root / "reports"))
        runner.check_config()
        self.assertTrue(any(f.status == "FAIL" for f in runner.findings))

    def test_malformed_ledger_is_failure(self):
        self.write_configs()
        (self.root / "handoffs/handoff.jsonl").write_text('{bad json}\n')
        runner = audit.Auditor(args(self.root / "reports"))
        runner.check_config()
        runner.check_ledger()
        self.assertTrue(any(f.check_id == "LEDGER-001" and f.status == "FAIL"
                            for f in runner.findings))

    def test_novel_duplicate_is_failure(self):
        self.write_configs()
        row1 = self.entry(7, "first")
        row2 = self.entry(7, "second")
        (self.root / "handoffs/handoff.jsonl").write_text(
            json.dumps(row1) + "\n" + json.dumps(row2) + "\n")
        runner = audit.Auditor(args(self.root / "reports"))
        runner.check_config()
        runner.check_ledger()
        self.assertTrue(any(f.check_id == "LEDGER-006" and f.status == "FAIL"
                            for f in runner.findings))

    def test_benign_path_reference_is_not_destructive(self):
        self.write_configs()
        row = self.entry(summary="Documentation describes MASTER_LIBRARY ownership.")
        (self.root / "handoffs/handoff.jsonl").write_text(json.dumps(row) + "\n")
        runner = audit.Auditor(args(self.root / "reports"))
        runner.check_config()
        runner.check_ledger()
        self.assertFalse(any(f.check_id == "POLICY-001" for f in runner.findings))

    def test_destructive_protected_path_is_failure(self):
        self.write_configs()
        row = self.entry(summary="run rm against MASTER_LIBRARY")
        (self.root / "handoffs/handoff.jsonl").write_text(json.dumps(row) + "\n")
        runner = audit.Auditor(args(self.root / "reports"))
        runner.check_config()
        runner.check_ledger()
        self.assertTrue(any(f.check_id == "POLICY-001" and f.status == "FAIL"
                            for f in runner.findings))

    def test_historical_ledger_secret_is_current_failure_and_redacted(self):
        self.write_configs()
        row = self.entry(summary="access_token=ghp_abcdefghijklmnopqrstuvwxyz123456")
        (self.root / "audit/rules.json").write_text(json.dumps({
            "schema_version": 1, "historical_ledger_cutoff_line": 99,
            "protected_paths": ["MASTER_LIBRARY"], "destructive_verbs": ["rm"],
            "policy_exceptions": [],
            "semantic_change_review": {"principles": ["keep evidence"]}}))
        (self.root / "handoffs/handoff.jsonl").write_text(json.dumps(row) + "\n")
        runner = audit.Auditor(args(self.root / "reports"))
        runner.check_config()
        runner.check_ledger()
        finding = next(f for f in runner.findings if f.check_id == "SECRET-LEDGER-001")
        self.assertEqual(finding.status, "FAIL")
        self.assertNotIn("ghp_", json.dumps(finding.evidence))

    def test_semantic_transport_failure_is_unknown(self):
        self.write_configs()
        runner = audit.Auditor(args(self.root / "reports", no_semantic=False))
        runner.entries = [dict(self.entry(), _audit_line=1)]
        with mock.patch.object(audit.urllib.request, "urlopen", side_effect=audit.urllib.error.URLError("down")):
            result = runner.semantic()
        self.assertIsNone(result)
        self.assertTrue(any(f.check_id == "SEMANTIC-001" and f.status == "UNKNOWN"
                            for f in runner.findings))
        evidence = list((self.root / "reports").glob("evidence-*.json"))
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0].stat().st_mode & 0o777, 0o600)

    def test_semantic_bad_calibration_is_unknown(self):
        self.write_configs()
        runner = audit.Auditor(args(self.root / "reports", no_semantic=False))
        runner.entries = [dict(self.entry(), _audit_line=1)]
        model_result = {
            "choices": [{"message": {"content": json.dumps({
                "calibration": {"completion_without_receipt": "PASS"},
                "status": "PASS", "findings": []
            })}}]
        }
        response = io.BytesIO(json.dumps(model_result).encode())
        with mock.patch.object(audit.urllib.request, "urlopen", return_value=response):
            result = runner.semantic()
        self.assertIsNone(result)
        self.assertTrue(any(f.check_id == "SEMANTIC-001" and f.status == "UNKNOWN"
                            for f in runner.findings))

    def test_conclusion_separates_history_from_current_advisory(self):
        self.write_configs()
        runner = audit.Auditor(args(self.root / "reports"))
        runner.add("LEDGER-006", "WARN", "Accepted historical duplicate ID", entry_id=41)
        runner.add("LEDGER-008", "WARN", "Backup litter exists beside the append-only ledger")
        conclusion = runner.build_conclusion(Counter(f.status for f in runner.findings))
        self.assertEqual(conclusion["verdict"], "PASS_WITH_ADVISORIES")
        self.assertFalse(conclusion["immediate_action_required"])
        self.assertEqual(conclusion["accepted_historical_warnings"], 1)
        self.assertEqual(conclusion["current_advisories"], 1)
        self.assertEqual(conclusion["review_recommended"][0]["check_id"], "LEDGER-008")

    def test_forced_failure_writes_marker_and_notification_command(self):
        self.write_configs()
        runner = audit.Auditor(args(self.root / "reports"))
        report = {
            "started_at": "2026-07-21T00:00:00Z", "exit_code": 1, "mode": "full",
            "auditor": {"working_sha256": "0" * 64},
            "conclusion": {
                "verdict": "FAIL", "summary": "Fixture violation; immediate action required.",
                "immediate_action_required": True, "established_violations": 1,
                "degraded_checks": 0, "accepted_historical_warnings": 0,
                "current_advisories": 0, "review_recommended": []
            },
            "findings": [],
        }
        markdown, _ = runner.write_report(report)
        marker = self.root / "reports/NEEDS_ATTENTION"
        self.assertTrue(marker.exists())
        self.assertIn("exit=1", marker.read_text())
        with mock.patch.object(audit.subprocess, "run") as invoked:
            audit.notify(markdown, 1)
        command = invoked.call_args.args[0]
        self.assertEqual(command[:2], ["/usr/bin/osascript", "-e"])
        self.assertIn("exit 1", command[2])


if __name__ == "__main__":
    unittest.main()
