import argparse
import importlib.util
import io
import json
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
