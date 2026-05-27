from __future__ import annotations

import json

from .baseline import finding_fingerprint
from .models import AuditSummary, Finding


SARIF_VERSION = "2.1.0"
DRIVER_NAME = "devops-validation-toolkit"


def _level(finding: Finding) -> str:
    severity = finding.severity.value
    if severity in {"critical", "high"}:
        return "error"
    if severity == "medium":
        return "warning"
    return "note"


def _result(finding: Finding) -> dict[str, object]:
    region: dict[str, int] = {}
    if finding.line is not None:
        region["startLine"] = finding.line
    location = {
        "physicalLocation": {
            "artifactLocation": {"uri": finding.path},
        }
    }
    if region:
        location["physicalLocation"]["region"] = region
    return {
        "ruleId": finding.rule_id,
        "level": _level(finding),
        "message": {"text": finding.title},
        "locations": [location],
        "partialFingerprints": {"primaryLocationLineHash": finding_fingerprint(finding)},
        "properties": {
            "severity": finding.severity.value,
            "recommendation": finding.recommendation or "",
        },
    }


def render_sarif(summary: AuditSummary) -> str:
    rules = {}
    for finding in summary.findings:
        rules[finding.rule_id] = {
            "id": finding.rule_id,
            "name": finding.rule_id,
            "shortDescription": {"text": finding.title},
            "help": {"text": finding.recommendation or finding.title},
            "properties": {"severity": finding.severity.value},
        }
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": DRIVER_NAME,
                        "informationUri": "https://github.com/mrsddq/infra-policy-lab-private-source",
                        "rules": [rules[key] for key in sorted(rules)],
                    }
                },
                "automationDetails": {"id": "devops-validation-toolkit"},
                "invocations": [
                    {
                        "executionSuccessful": not summary.failed,
                        "properties": {
                            "scannedFiles": summary.scanned_files,
                            "riskScore": summary.risk_score,
                        },
                    }
                ],
                "results": [_result(finding) for finding in summary.findings],
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
