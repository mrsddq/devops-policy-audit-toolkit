from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

from .models import Finding, Severity, coerce_severity


@dataclass(frozen=True)
class PolicyOverride:
    rule_id: str
    path_pattern: str
    reason: str
    expires: str | None = None

    def matches(self, finding: Finding) -> bool:
        return self.rule_id == finding.rule_id and fnmatch(finding.path, self.path_pattern)


@dataclass(frozen=True)
class AuditPolicy:
    fail_on: tuple[Severity, ...] = (Severity.HIGH, Severity.CRITICAL)
    ignored_paths: tuple[str, ...] = ()
    overrides: tuple[PolicyOverride, ...] = ()

    def is_ignored_path(self, path: str) -> bool:
        return any(fnmatch(path, pattern) for pattern in self.ignored_paths)

    def is_overridden(self, finding: Finding) -> bool:
        return any(override.matches(finding) for override in self.overrides)

    def filter_findings(self, findings: Iterable[Finding]) -> list[Finding]:
        results: list[Finding] = []
        for finding in findings:
            if self.is_ignored_path(finding.path):
                continue
            if self.is_overridden(finding):
                continue
            results.append(finding)
        return results

    def should_fail(self, findings: Iterable[Finding]) -> bool:
        gate = {coerce_severity(item) for item in self.fail_on}
        return any(coerce_severity(f.severity) in gate for f in findings)


def load_policy(path: str | Path | None) -> AuditPolicy:
    if path is None:
        return AuditPolicy()
    policy_path = Path(path)
    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")
    import json

    raw = json.loads(policy_path.read_text(encoding="utf-8"))
    fail_on = tuple(coerce_severity(value) for value in raw.get("fail_on", ["high", "critical"]))
    ignored_paths = tuple(str(value) for value in raw.get("ignored_paths", []))
    overrides = tuple(
        PolicyOverride(
            rule_id=str(item["rule_id"]),
            path_pattern=str(item["path_pattern"]),
            reason=str(item.get("reason", "documented exception")),
            expires=item.get("expires"),
        )
        for item in raw.get("overrides", [])
    )
    return AuditPolicy(fail_on=fail_on, ignored_paths=ignored_paths, overrides=overrides)
