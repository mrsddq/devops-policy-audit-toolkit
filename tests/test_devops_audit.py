import tempfile
import unittest
from pathlib import Path

from devops_toolkit.audit import run_audit
from devops_toolkit.checks import check_dockerfiles
from devops_toolkit.reporting import format_json_report, format_text_report

ROOT = Path(__file__).resolve().parents[1]


class DevOpsAuditTests(unittest.TestCase):
    def test_audit_counts_repository_artifacts(self):
        result = run_audit(ROOT)

        self.assertGreater(len(result.inventory.terraform_files), 0)
        self.assertGreater(len(result.inventory.yaml_files), 0)
        self.assertGreater(len(result.inventory.groovy_files), 0)
        self.assertGreaterEqual(len(result.inventory.dockerfiles), 1)

    def test_audit_dockerfiles_reports_unpinned_base_images(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            dockerfile = root / "Dockerfile"
            dockerfile.write_text("FROM nginx\n", encoding="utf-8")

            findings = check_dockerfiles((dockerfile,))

        self.assertEqual(findings[0].message, "base image is not pinned")

    def test_text_report_contains_summary(self):
        report = run_audit(ROOT)
        text = format_text_report(report)

        self.assertIn("Terraform files:", text)
        self.assertIn("YAML files:", text)

    def test_json_report_contains_findings_key(self):
        report = run_audit(ROOT)
        text = format_json_report(report)

        self.assertIn('"summary"', text)
        self.assertIn('"findings"', text)


if __name__ == "__main__":
    unittest.main()
