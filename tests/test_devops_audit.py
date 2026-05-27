import tempfile
import unittest
from pathlib import Path

from scripts.devops_audit import audit_dockerfiles, run_audit


class DevOpsAuditTests(unittest.TestCase):
    def test_audit_counts_repository_artifacts(self):
        result = run_audit()

        self.assertGreater(result.terraform_files, 0)
        self.assertGreater(result.yaml_files, 0)
        self.assertGreater(result.groovy_files, 0)
        self.assertGreaterEqual(result.dockerfiles, 1)

    def test_audit_dockerfiles_reports_unpinned_base_images(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            dockerfile = root / "Dockerfile"
            dockerfile.write_text("FROM nginx\n", encoding="utf-8")

            warnings = audit_dockerfiles([dockerfile], root)

        self.assertEqual(warnings, ["Dockerfile uses an unpinned base image"])


if __name__ == "__main__":
    unittest.main()
