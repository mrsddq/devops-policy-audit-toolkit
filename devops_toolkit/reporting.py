from __future__ import annotations

import json
from html import escape
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


def render_html(summary: AuditSummary) -> str:
    severity_rows = "\n".join(
        f"<tr><td>{escape(severity)}</td><td>{count}</td></tr>"
        for severity, count in summary.by_severity.items()
    )
    finding_rows = "\n".join(
        "<tr>"
        f"<td>{escape(finding.rule_id)}</td>"
        f"<td>{escape(finding.severity.value)}</td>"
        f"<td>{escape(finding.path)}</td>"
        f"<td>{'' if finding.line is None else finding.line}</td>"
        f"<td>{escape(finding.title)}</td>"
        f"<td>{escape(finding.recommendation or '')}</td>"
        "</tr>"
        for finding in summary.findings
    )
    if not finding_rows:
        finding_rows = "<tr><td colspan=\"6\">No findings detected.</td></tr>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DevOps Repository Audit Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 24px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .failed {{ color: #b91c1c; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>DevOps Repository Audit Report</h1>
  <p>Root: <code>{escape(summary.root)}</code></p>
  <p>Scanned files: <strong>{summary.scanned_files}</strong></p>
  <p>Risk score: <strong>{summary.risk_score}</strong></p>
  <p>Gate failed: <span class="failed">{str(summary.failed).lower()}</span></p>
  <h2>Severity Counts</h2>
  <table>
    <thead><tr><th>Severity</th><th>Count</th></tr></thead>
    <tbody>{severity_rows}</tbody>
  </table>
  <h2>Findings</h2>
  <table>
    <thead><tr><th>Rule</th><th>Severity</th><th>File</th><th>Line</th><th>Finding</th><th>Recommendation</th></tr></thead>
    <tbody>{finding_rows}</tbody>
  </table>
</body>
</html>
"""


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
