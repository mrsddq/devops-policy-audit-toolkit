import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from devops_toolkit.cli import main


class CliTests(unittest.TestCase):
    def test_cli_writes_json_report(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
            output = Path(directory) / "report.json"

            exit_code = main([str(root), "--format", "json", "--output", str(output)])

            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["scanned_files"], 1)
        self.assertEqual(payload["findings"][0]["rule_id"], "DOCKER_NO_USER")

    def test_cli_honors_policy_config(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
            config = Path(directory) / "config.json"
            config.write_text(
                json.dumps({"policy": {"fail_on": ["critical"], "ignored_paths": [], "overrides": []}}),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                exit_code = main([str(root), "--config", str(config), "--fail-on-high"])

        self.assertEqual(exit_code, 0)

    def test_cli_writes_and_uses_baseline(self):
        with TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
            baseline = Path(directory) / "baseline.json"
            report = Path(directory) / "report.json"

            with redirect_stdout(StringIO()):
                self.assertEqual(main([str(root), "--write-baseline", str(baseline)]), 0)
            exit_code = main([str(root), "--baseline", str(baseline), "--format", "json", "--output", str(report)])
            payload = json.loads(report.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["findings"], [])


if __name__ == "__main__":
    unittest.main()
