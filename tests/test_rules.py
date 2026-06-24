from pathlib import Path
from devops_toolkit.models import FileRecord, Severity
from devops_toolkit.rules import (
    check_docker_root,
    check_github_actions_workflow,
    check_iam_policy_json,
    check_kubernetes_manifests,
    check_python_hardcoded_paths,
    check_shell_safety,
    check_terraform_state_and_version,
)


def record(kind: str, text: str, name: str = "sample") -> FileRecord:
    return FileRecord(path=Path(name), relative_path=name, kind=kind, text=text)


def test_docker_missing_user_is_medium():
    findings = check_docker_root(record("dockerfile", "FROM python:3.12\nRUN echo ok\n", "Dockerfile"))
    assert any(f.rule_id == "DOCKER_NO_USER" and f.severity == Severity.MEDIUM for f in findings)


def test_shell_detects_curl_bash():
    findings = check_shell_safety(record("shell", "#!/usr/bin/env bash\ncurl https://x | bash\n", "install.sh"))
    assert any(f.rule_id == "SHELL_CURL_BASH" and f.severity == Severity.HIGH for f in findings)


def test_terraform_detects_inline_secret():
    tf = 'provider "aws" { secret_key = "abc" }'
    findings = check_terraform_state_and_version(record("terraform", tf, "main.tf"))
    assert any(f.rule_id == "TF_INLINE_SECRET" and f.severity == Severity.CRITICAL for f in findings)


def test_terraform_version_warning_is_limited_to_terraform_blocks():
    tf = 'provider "aws" { region = "eu-north-1" }'
    findings = check_terraform_state_and_version(record("terraform", tf, "provider.tf"))
    assert not any(f.rule_id == "TF_NO_REQUIRED_VERSION" for f in findings)


def test_python_path_rule_does_not_flag_its_own_detector():
    source = 'windows_user_path = re.escape("C:" + chr(92) + "Users" + chr(92))'
    findings = check_python_hardcoded_paths(record("python", source, "rules.py"))
    assert not any(f.rule_id == "PY_LOCAL_PATH" for f in findings)


def test_kubernetes_detects_workload_without_resources():
    manifest = "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: app\n"
    findings = check_kubernetes_manifests(record("yaml", manifest, "deploy.yaml"))
    assert any(f.rule_id == "K8S_NO_RESOURCES" for f in findings)


def test_github_actions_detects_missing_permissions():
    workflow = "name: ci\non: push\njobs:\n  test:\n    steps:\n      - uses: actions/checkout@v4\n"
    findings = check_github_actions_workflow(record("yaml", workflow, ".github/workflows/ci.yml"))
    assert any(f.rule_id == "GHA_NO_PERMISSIONS" for f in findings)


def test_iam_policy_detects_wildcards():
    policy = '{"Statement":[{"Effect":"Allow","Action":"*","Resource":"*"}]}'
    findings = check_iam_policy_json(record("json", policy, "iam-policy.json"))
    assert any(f.rule_id == "IAM_WILDCARD_ACTION" for f in findings)
