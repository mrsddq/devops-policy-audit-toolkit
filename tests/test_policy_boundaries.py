from datetime import date
import json

import pytest

from devops_toolkit.baseline import write_baseline
from devops_toolkit.cli import main
from devops_toolkit.config import load_config, policy_from_mapping
from devops_toolkit.inventory import build_inventory
from devops_toolkit.models import Finding, Severity
from devops_toolkit.policy import PolicyOverride


def test_override_expires_after_the_named_utc_day():
    finding = Finding(rule_id="X", title="unsafe", path="app.yaml", severity=Severity.HIGH)
    override = PolicyOverride("X", "*.yaml", "migration window", "2026-09-17")
    assert override.matches(finding, today=date(2026, 9, 17))
    assert not override.matches(finding, today=date(2026, 9, 18))
    assert not override.matches(
        Finding(rule_id="Y", title="unsafe", path="app.yaml"), today=date(2026, 9, 17)
    )


@pytest.mark.parametrize(
    "raw",
    [
        {"policy": []},
        {"fail_on": ["hihg"]},
        {"fail_on": "high"},
        {"ignored_paths": "*"},
        {"overrides": [{"rule_id": "X", "path_pattern": "*"}]},
        {"overrides": [{"rule_id": "X", "path_pattern": "*", "reason": ""}]},
        {
            "overrides": [
                {"rule_id": "X", "path_pattern": "*", "reason": "test", "expires": "later"}
            ]
        },
    ],
)
def test_invalid_policy_cannot_silently_disable_findings(raw):
    with pytest.raises(ValueError):
        policy_from_mapping(raw)


def test_invalid_yaml_and_format_are_cli_errors(tmp_path, capsys):
    config = tmp_path / "policy.yaml"
    config.write_text("policy: [broken", encoding="utf-8")
    assert main([str(tmp_path), "--config", str(config)]) == 2
    assert "Invalid YAML" in capsys.readouterr().err
    config.write_text("default_format: typo", encoding="utf-8")
    with pytest.raises(ValueError, match="default_format"):
        load_config(config)


def test_invalid_baseline_fails_without_overwriting_it(tmp_path, capsys):
    baseline = tmp_path / "baseline.json"
    original = '{"version": 1, "findings": [{"fingerprint": "bad"}]}'
    baseline.write_text(original, encoding="utf-8")
    assert (
        main([str(tmp_path), "--baseline", str(baseline), "--write-baseline", str(baseline)]) == 2
    )
    assert baseline.read_text(encoding="utf-8") == original
    assert "Invalid baseline" in capsys.readouterr().err


def test_unhashable_output_format_is_a_controlled_cli_error(tmp_path, capsys):
    config = tmp_path / "config.json"
    config.write_text('{"default_format": []}', encoding="utf-8")
    assert main([str(tmp_path), "--config", str(config)]) == 2
    assert "default_format" in capsys.readouterr().err


def test_refreshing_baseline_does_not_hide_new_findings(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "Dockerfile").write_text("FROM python:latest\n", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    write_baseline(baseline, [])
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"policy": {"fail_on": ["medium"]}}), encoding="utf-8")
    assert (
        main(
            [
                str(repo),
                "--baseline",
                str(baseline),
                "--write-baseline",
                str(baseline),
                "--config",
                str(config),
                "--format",
                "json",
                "--fail-on-high",
            ]
        )
        == 2
    )
    report = json.loads(capsys.readouterr().out)
    assert report["findings"]


def test_inventory_skips_symlinks_and_handles_named_parent(tmp_path):
    repo = tmp_path / "build" / "repo"
    repo.mkdir(parents=True)
    (repo / "Dockerfile").write_text("FROM python:3.12\nUSER 1000\n", encoding="utf-8")
    outside = tmp_path / "outside.py"
    outside.write_text("private_value = 'do not scan'", encoding="utf-8")
    (repo / "linked.py").symlink_to(outside)
    linked_dir = tmp_path / "outside_dir"
    linked_dir.mkdir()
    (linked_dir / "hidden.py").write_text("pass", encoding="utf-8")
    (repo / "linked_dir").symlink_to(linked_dir, target_is_directory=True)
    records = build_inventory(repo)
    assert [record.relative_path for record in records] == ["Dockerfile"]
