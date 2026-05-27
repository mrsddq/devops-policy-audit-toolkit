from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import Finding


BASELINE_VERSION = 1


@dataclass(frozen=True)
class BaselineEntry:
    fingerprint: str
    rule_id: str
    path: str
    line: int | None
    title: str


def finding_fingerprint(finding: Finding) -> str:
    payload = "|".join(
        [
            finding.rule_id,
            finding.path,
            "" if finding.line is None else str(finding.line),
            finding.title,
            finding.evidence or "",
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_baseline(findings: Iterable[Finding]) -> dict[str, object]:
    entries = [
        BaselineEntry(
            fingerprint=finding_fingerprint(finding),
            rule_id=finding.rule_id,
            path=finding.path,
            line=finding.line,
            title=finding.title,
        )
        for finding in sorted(findings, key=lambda item: (item.path, item.rule_id, item.line or 0))
    ]
    return {
        "version": BASELINE_VERSION,
        "findings": [entry.__dict__ for entry in entries],
    }


def write_baseline(path: str | Path, findings: Iterable[Finding]) -> None:
    baseline_path = Path(path)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(json.dumps(build_baseline(findings), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_baseline(path: str | Path) -> set[str]:
    baseline_path = Path(path)
    raw = json.loads(baseline_path.read_text(encoding="utf-8"))
    if int(raw.get("version", 0)) != BASELINE_VERSION:
        raise ValueError(f"Unsupported baseline version in {baseline_path}")
    return {str(item["fingerprint"]) for item in raw.get("findings", [])}


def filter_new_findings(findings: Iterable[Finding], baseline_path: str | Path | None) -> list[Finding]:
    items = list(findings)
    if baseline_path is None:
        return items
    known = load_baseline(baseline_path)
    return [finding for finding in items if finding_fingerprint(finding) not in known]
