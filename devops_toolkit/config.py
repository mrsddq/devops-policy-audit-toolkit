from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .policy import AuditPolicy, PolicyOverride
from .models import Severity


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
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML config: {path}") from exc
        if data is None:
            data = {}
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain an object: {path}")
    return data


def policy_from_mapping(raw: dict[str, Any]) -> AuditPolicy:
    policy_raw = raw.get("policy", raw)
    if not isinstance(policy_raw, dict):
        raise ValueError("policy must be an object")
    for key in ("fail_on", "ignored_paths", "overrides"):
        if key in policy_raw and not isinstance(policy_raw[key], list):
            raise ValueError(f"policy.{key} must be a list")
    try:
        fail_on = tuple(
            Severity(value) for value in policy_raw.get("fail_on", ["high", "critical"])
        )
    except (ValueError, TypeError) as exc:
        raise ValueError("policy.fail_on contains an unknown severity") from exc
    ignored_paths = tuple(policy_raw.get("ignored_paths", []))
    if not all(isinstance(value, str) and value.strip() for value in ignored_paths):
        raise ValueError("policy.ignored_paths must contain non-empty strings")
    for item in policy_raw.get("overrides", []):
        if not isinstance(item, dict) or not {"rule_id", "path_pattern", "reason"} <= item.keys():
            raise ValueError("each override requires rule_id, path_pattern and reason")
    overrides = tuple(
        PolicyOverride(
            rule_id=item["rule_id"],
            path_pattern=item["path_pattern"],
            reason=item["reason"],
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
    if not isinstance(raw.get("default_format", "text"), str) or raw.get(
        "default_format", "text"
    ) not in {"text", "json", "markdown", "html", "sarif"}:
        raise ValueError("default_format must be text, json, markdown, html or sarif")
    return AuditConfig(
        policy=policy_from_mapping(raw),
        default_format=str(raw.get("default_format", "text")),
        report_directory=str(raw.get("report_directory", "reports")),
    )
