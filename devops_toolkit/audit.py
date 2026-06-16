from __future__ import annotations

from pathlib import Path
from .inventory import build_inventory, build_legacy_inventory
from .models import AuditSummary, Finding
from .rules import RULES


def audit_repository(root: str | Path) -> AuditSummary:
    base = Path(root).resolve()
    if not base.exists():
        raise FileNotFoundError(f"scan root does not exist: {base}")
    if not base.is_dir():
        raise NotADirectoryError(f"scan root is not a directory: {base}")

    records = build_inventory(base)
    findings: list[Finding] = []
    for record in records:
        for rule in RULES:
            if record.kind in rule.kinds:
                findings.extend(rule.check(record))
    summary = AuditSummary(root=str(base), scanned_files=len(records), findings=findings, inventory=build_legacy_inventory(base))
    summary.findings = summary.unique_findings()
    return summary


def run_audit(root: str | Path) -> AuditSummary:
    return audit_repository(root)
