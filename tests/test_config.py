import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from devops_toolkit.config import load_config
from devops_toolkit.models import Finding, Severity


class ConfigTests(unittest.TestCase):
    def test_json_config_loads_policy_and_defaults(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            path.write_text(
                json.dumps(
                    {
                        "default_format": "json",
                        "report_directory": "out",
                        "policy": {
                            "fail_on": ["critical"],
                            "ignored_paths": ["docs/*"],
                            "overrides": [
                                {
                                    "rule_id": "K8S_NO_RESOURCES",
                                    "path_pattern": "labs/*",
                                    "reason": "documented lab exception",
                                }
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )

            config = load_config(path)

        self.assertEqual(config.default_format, "json")
        self.assertEqual(config.report_directory, "out")
        self.assertFalse(config.policy.should_fail([Finding("X", "app.py", "issue", Severity.HIGH)]))
        self.assertTrue(config.policy.is_ignored_path("docs/readme.md"))


if __name__ == "__main__":
    unittest.main()
