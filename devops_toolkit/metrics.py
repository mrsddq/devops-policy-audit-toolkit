from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable

from .models import Finding, Severity, coerce_severity


@dataclass(frozen=True)
class FindingMetrics:
    total: int
    by_rule: dict[str, int]
    by_severity: dict[str, int]
    by_directory: dict[str, int]
    highest_severity: Severity

    def top_rules(self, limit: int = 5) -> list[tuple[str, int]]:
        return sorted(self.by_rule.items(), key=lambda item: (-item[1], item[0]))[:limit]

    def top_directories(self, limit: int = 5) -> list[tuple[str, int]]:
        return sorted(self.by_directory.items(), key=lambda item: (-item[1], item[0]))[:limit]


def parent_bucket(path: str) -> str:
    pure = PurePosixPath(path)
    if len(pure.parts) <= 1:
        return "."
    return pure.parts[0]


def compute_metrics(findings: Iterable[Finding]) -> FindingMetrics:
    items = list(findings)
    by_rule: Counter[str] = Counter()
    by_severity: Counter[str] = Counter()
    by_directory: Counter[str] = Counter()
    highest = Severity.INFO
    for finding in items:
        sev = coerce_severity(finding.severity)
        by_rule[finding.rule_id] += 1
        by_severity[sev.value] += 1
        by_directory[parent_bucket(finding.path)] += 1
        if sev.score > highest.score:
            highest = sev
    return FindingMetrics(
        total=len(items),
        by_rule=dict(by_rule),
        by_severity={severity.value: by_severity.get(severity.value, 0) for severity in Severity},
        by_directory=dict(by_directory),
        highest_severity=highest,
    )


def group_by_rule(findings: Iterable[Finding]) -> dict[str, list[Finding]]:
    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        grouped[finding.rule_id].append(finding)
    return dict(grouped)


def group_by_file(findings: Iterable[Finding]) -> dict[str, list[Finding]]:
    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        grouped[finding.path].append(finding)
    return dict(grouped)
