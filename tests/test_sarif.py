import json
import unittest

from devops_toolkit.models import AuditSummary, Finding, Severity
from devops_toolkit.sarif import render_sarif


class SarifTests(unittest.TestCase):
    def test_sarif_output_contains_tool_and_result(self):
        summary = AuditSummary(
            root=".",
            scanned_files=1,
            findings=[
                Finding(
                    rule_id="DOCKER_NO_USER",
                    title="Dockerfile has no non-root USER instruction",
                    severity=Severity.MEDIUM,
                    path="Dockerfile",
                    line=1,
                    recommendation="Add a non-root user.",
                )
            ],
        )

        payload = json.loads(render_sarif(summary))

        self.assertEqual(payload["version"], "2.1.0")
        self.assertEqual(payload["runs"][0]["tool"]["driver"]["name"], "devops-validation-toolkit")
        self.assertEqual(payload["runs"][0]["results"][0]["ruleId"], "DOCKER_NO_USER")


if __name__ == "__main__":
    unittest.main()
