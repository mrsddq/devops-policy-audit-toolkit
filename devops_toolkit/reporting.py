from __future__ import annotations

import json
from .models import AuditSummary, Finding


def finding_to_dict(finding: Finding) -> dict[str, object]:
    return {
        "rule_id": finding.rule_id,
        "title": finding.title,
        "severity": finding.severity.value,
        "path": finding.path,
        "line": finding.line,
        "evidence": finding.evidence,
        "recommendation": finding.recommendation,
        "metadata": finding.metadata,
    }


def render_json(summary: AuditSummary) -> str:
    payload = {
        "summary": {
            "root": summary.root,
            "scanned_files": summary.scanned_files,
            "risk_score": summary.risk_score,
            "failed": summary.failed,
            "by_severity": summary.by_severity,
        },
        "root": summary.root,
        "scanned_files": summary.scanned_files,
        "risk_score": summary.risk_score,
        "failed": summary.failed,
        "by_severity": summary.by_severity,
        "findings": [finding_to_dict(f) for f in summary.findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_markdown(summary: AuditSummary) -> str:
    lines = [
        "# DevOps Repository Audit Report",
        "",
        f"Root: `{summary.root}`",
        f"Scanned files: **{summary.scanned_files}**",
        f"Risk score: **{summary.risk_score}**",
        f"Gate failed: **{str(summary.failed).lower()}**",
        "",
        "## Severity Counts",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]
    for severity, count in summary.by_severity.items():
        lines.append(f"| {severity} | {count} |")
    lines.extend(["", "## Findings", ""])
    if not summary.findings:
        lines.append("No findings detected.")
        return "\n".join(lines) + "\n"
    lines.append("| Rule | Severity | File | Line | Recommendation |")
    lines.append("|---|---|---|---:|---|")
    for finding in summary.findings:
        line = "" if finding.line is None else str(finding.line)
        rec = (finding.recommendation or "").replace("|", r"\|")
        lines.append(f"| {finding.rule_id} | {finding.severity.value} | `{finding.path}` | {line} | {rec} |")
    return "\n".join(lines) + "\n"


def render_text(summary: AuditSummary) -> str:
    lines = [
        "DevOps repository audit",
        f"Root: {summary.root}",
        f"Scanned files: {summary.scanned_files}",
        f"Risk score: {summary.risk_score}",
        f"Failed: {summary.failed}",
        "",
    ]
    for finding in summary.findings:
        location = finding.path if finding.line is None else f"{finding.path}:{finding.line}"
        lines.append(f"[{finding.severity.value.upper()}] {finding.rule_id} {location} - {finding.title}")
        if finding.recommendation:
            lines.append(f"  fix: {finding.recommendation}")
    return "\n".join(lines) + "\n"


def format_json_report(summary: AuditSummary) -> str:
    return render_json(summary)


def format_text_report(summary: AuditSummary) -> str:
    if summary.inventory is None:
        return render_text(summary)
    inv = summary.inventory
    prefix = "\n".join([
        "Repository summary",
        f"Terraform files: {len(inv.terraform_files)}",
        f"YAML files: {len(inv.yaml_files)}",
        f"Groovy files: {len(inv.groovy_files)}",
        f"Dockerfiles: {len(inv.dockerfiles)}",
        "",
    ])
    return prefix + render_text(summary)
