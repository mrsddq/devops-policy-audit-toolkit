from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .policy import AuditPolicy, PolicyOverride
from .models import Severity, coerce_severity


@dataclass(frozen=True)
class AuditConfig:
    policy: AuditPolicy
    default_format: str = "text"
    report_directory: str = "reports"


def _load_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("YAML config requires PyYAML to be installed") from exc
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain an object: {path}")
    return data


def policy_from_mapping(raw: dict[str, Any]) -> AuditPolicy:
    policy_raw = raw.get("policy", raw)
    fail_on = tuple(coerce_severity(value) for value in policy_raw.get("fail_on", ["high", "critical"]))
    ignored_paths = tuple(str(value) for value in policy_raw.get("ignored_paths", []))
    overrides = tuple(
        PolicyOverride(
            rule_id=str(item["rule_id"]),
            path_pattern=str(item["path_pattern"]),
            reason=str(item.get("reason", "documented exception")),
            expires=item.get("expires"),
        )
        for item in policy_raw.get("overrides", [])
    )
    return AuditPolicy(fail_on=fail_on, ignored_paths=ignored_paths, overrides=overrides)


def load_config(path: str | Path | None) -> AuditConfig:
    if path is None:
        return AuditConfig(policy=AuditPolicy())
    config_path = Path(path)
    raw = _load_mapping(config_path)
    return AuditConfig(
        policy=policy_from_mapping(raw),
        default_format=str(raw.get("default_format", "text")),
        report_directory=str(raw.get("report_directory", "reports")),
    )
