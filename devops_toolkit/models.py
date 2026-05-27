from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def score(self) -> int:
        return {Severity.INFO: 0, Severity.LOW: 1, Severity.MEDIUM: 3, Severity.HIGH: 7, Severity.CRITICAL: 10}[self]


def coerce_severity(value: Severity | str | None) -> Severity:
    if isinstance(value, Severity):
        return value
    if value is None:
        return Severity.LOW
    normalized = str(value).lower()
    return Severity(normalized) if normalized in {s.value for s in Severity} else Severity.LOW


@dataclass(frozen=True, init=False)
class Finding:
    rule_id: str
    title: str
    severity: Severity
    path: str
    line: int | None = None
    evidence: str | None = None
    recommendation: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # New API: Finding(rule_id=..., title=..., severity=..., path=...)
        if kwargs:
            rule_id = kwargs.get("rule_id")
            title = kwargs.get("title")
            severity = coerce_severity(kwargs.get("severity", Severity.LOW))
            path = kwargs.get("path")
            line = kwargs.get("line")
            evidence = kwargs.get("evidence")
            recommendation = kwargs.get("recommendation")
            metadata = kwargs.get("metadata", {})
        # Compatibility API: Finding(check, path, message, severity="low")
        elif len(args) >= 3:
            rule_id = str(args[0])
            path = str(args[1])
            title = str(args[2])
            severity = coerce_severity(args[3] if len(args) > 3 else Severity.LOW)
            line = None
            evidence = None
            recommendation = None
            metadata = {}
        else:
            raise TypeError("Finding requires either keyword fields or check, path, message arguments")
        object.__setattr__(self, "rule_id", str(rule_id))
        object.__setattr__(self, "title", str(title))
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "path", str(path))
        object.__setattr__(self, "line", line)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "recommendation", recommendation)
        object.__setattr__(self, "metadata", metadata)

    @property
    def check(self) -> str:
        return self.rule_id

    @property
    def message(self) -> str:
        return self.title

    def key(self) -> tuple[str, str, int | None, str | None]:
        return (self.rule_id, self.path, self.line, self.evidence)


@dataclass(frozen=True)
class FileRecord:
    path: Path
    relative_path: str
    kind: str
    text: str

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()


@dataclass(frozen=True)
class FileInventory:
    terraform_files: tuple[Path, ...]
    yaml_files: tuple[Path, ...]
    groovy_files: tuple[Path, ...]
    markdown_files: tuple[Path, ...]
    dockerfiles: tuple[Path, ...]
    other_files: tuple[Path, ...]


@dataclass
class AuditSummary:
    root: str
    scanned_files: int
    findings: list[Finding]
    inventory: FileInventory | None = None

    @property
    def risk_score(self) -> int:
        return sum(coerce_severity(f.severity).score for f in self.findings)

    @property
    def by_severity(self) -> dict[str, int]:
        counts = {severity.value: 0 for severity in Severity}
        for finding in self.findings:
            counts[coerce_severity(finding.severity).value] += 1
        return counts

    @property
    def failed(self) -> bool:
        return any(coerce_severity(f.severity) in {Severity.HIGH, Severity.CRITICAL} for f in self.findings)

    def unique_findings(self) -> list[Finding]:
        seen: set[tuple[str, str, int | None, str | None]] = set()
        unique: list[Finding] = []
        for finding in self.findings:
            if finding.key() in seen:
                continue
            seen.add(finding.key())
            unique.append(finding)
        return unique


AuditResult = AuditSummary


def normalize_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def flatten(items: Iterable[Iterable[Finding]]) -> list[Finding]:
    results: list[Finding] = []
    for group in items:
        results.extend(group)
    return results
