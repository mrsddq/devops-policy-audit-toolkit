from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
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

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (self.rule_id, self.path_pattern, self.reason)
        ):
            raise ValueError("override rule_id, path_pattern and reason must be non-empty strings")
        if self.expires is not None:
            if not isinstance(self.expires, str):
                raise ValueError("override expires must be a YYYY-MM-DD string")
            try:
                parsed = date.fromisoformat(self.expires)
            except ValueError as exc:
                raise ValueError("override expires must be a YYYY-MM-DD string") from exc
            if parsed.isoformat() != self.expires:
                raise ValueError("override expires must be a YYYY-MM-DD string")

    def matches(self, finding: Finding, *, today: date | None = None) -> bool:
        current_date = today if today is not None else datetime.now(timezone.utc).date()
        if self.expires is not None and date.fromisoformat(self.expires) < current_date:
            return False
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
    from .config import policy_from_mapping

    import json

    return policy_from_mapping(json.loads(policy_path.read_text(encoding="utf-8")))
