import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from devops_toolkit.baseline import filter_new_findings, finding_fingerprint, write_baseline
from devops_toolkit.models import Finding, Severity


def finding(rule_id="RULE", path="Dockerfile", line=1):
    return Finding(rule_id=rule_id, title="issue", severity=Severity.HIGH, path=path, line=line)


class BaselineTests(unittest.TestCase):
    def test_fingerprint_is_stable_for_same_finding(self):
        self.assertEqual(finding_fingerprint(finding()), finding_fingerprint(finding()))

    def test_baseline_filters_existing_findings(self):
        with TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.json"
            existing = finding()
            new = finding("OTHER", "main.tf", None)
            write_baseline(baseline, [existing])

            remaining = filter_new_findings([existing, new], baseline)

        self.assertEqual([item.rule_id for item in remaining], ["OTHER"])

    def test_baseline_file_has_versioned_schema(self):
        with TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.json"
            write_baseline(baseline, [finding()])
            payload = json.loads(baseline.read_text(encoding="utf-8"))

        self.assertEqual(payload["version"], 1)
        self.assertIn("fingerprint", payload["findings"][0])


if __name__ == "__main__":
    unittest.main()
