import json
from dataclasses import asdict

from .models import AuditReport


def format_text_report(report: AuditReport, include_info: bool = False) -> str:
    lines = report.summary_lines()
    visible_findings = [
        finding for finding in report.findings if include_info or finding.severity != "info"
    ]

    if visible_findings:
        lines.append("Findings:")
        lines.extend(finding.format(report.root) for finding in visible_findings)
    else:
        lines.append("Audit passed with no warnings.")
    return "\n".join(lines)


def format_json_report(report: AuditReport) -> str:
    payload = {
        "summary": {
            "terraform_files": len(report.inventory.terraform_files),
            "yaml_files": len(report.inventory.yaml_files),
            "groovy_files": len(report.inventory.groovy_files),
            "markdown_files": len(report.inventory.markdown_files),
            "dockerfiles": len(report.inventory.dockerfiles),
            "total_files": report.inventory.total_files,
        },
        "findings": [
            {
                **asdict(finding),
                "path": str(finding.path.relative_to(report.root)),
            }
            for finding in report.findings
        ],
    }
    return json.dumps(payload, indent=2)

