from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from .models import FileRecord, Finding, Severity

Check = Callable[[FileRecord], list[Finding]]


@dataclass(frozen=True)
class Rule:
    rule_id: str
    description: str
    kinds: set[str]
    check: Check


def finding(record: FileRecord, rule_id: str, title: str, severity: Severity, line: int | None, evidence: str | None, recommendation: str) -> Finding:
    return Finding(rule_id=rule_id, title=title, severity=severity, path=record.relative_path, line=line, evidence=evidence, recommendation=recommendation)


def check_docker_root(record: FileRecord) -> list[Finding]:
    if record.kind != "dockerfile":
        return []
    results: list[Finding] = []
    has_user = False
    for idx, line in enumerate(record.lines, start=1):
        stripped = line.strip()
        if stripped.upper().startswith("USER "):
            has_user = True
            if stripped.lower() in {"user root", "user 0"}:
                results.append(finding(record, "DOCKER_USER_ROOT", "Container explicitly runs as root", Severity.HIGH, idx, stripped, "Create and switch to a non-root runtime user."))
    if not has_user:
        results.append(finding(record, "DOCKER_NO_USER", "Dockerfile has no non-root USER instruction", Severity.MEDIUM, None, None, "Add a non-root USER instruction after package installation."))
    return results


def check_docker_pin_versions(record: FileRecord) -> list[Finding]:
    if record.kind != "dockerfile":
        return []
    results: list[Finding] = []
    for idx, line in enumerate(record.lines, start=1):
        stripped = line.strip()
        if stripped.upper().startswith("FROM ") and ":latest" in stripped.lower():
            results.append(finding(record, "DOCKER_LATEST_TAG", "Docker image uses latest tag", Severity.MEDIUM, idx, stripped, "Pin base images to immutable version tags or digests."))
        if re.search(r"apt-get\s+install", stripped) and "--no-install-recommends" not in stripped:
            results.append(finding(record, "DOCKER_APT_RECOMMENDS", "apt install lacks --no-install-recommends", Severity.LOW, idx, stripped, "Use --no-install-recommends and clean apt lists in the same layer."))
    return results


def check_shell_safety(record: FileRecord) -> list[Finding]:
    if record.kind != "shell":
        return []
    lines = record.lines
    results: list[Finding] = []
    if not any("set -e" in line or "set -euo pipefail" in line for line in lines[:10]):
        results.append(finding(record, "SHELL_NO_STRICT_MODE", "Shell script does not enable strict mode", Severity.MEDIUM, None, None, "Add set -euo pipefail near the top of the script."))
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if re.search(r"curl .*\|\s*(sudo\s+)?bash", stripped):
            results.append(finding(record, "SHELL_CURL_BASH", "Script pipes downloaded content into bash", Severity.HIGH, idx, stripped, "Download, checksum, inspect, then execute remote installation scripts."))
        if "chmod 777" in stripped:
            results.append(finding(record, "SHELL_WORLD_WRITABLE", "Script applies chmod 777", Severity.HIGH, idx, stripped, "Use the narrowest permission needed, commonly 640, 750, or 755."))
    return results


def check_terraform_state_and_version(record: FileRecord) -> list[Finding]:
    if record.kind != "terraform":
        return []
    text = record.text
    results: list[Finding] = []
    if "terraform" in text and "required_version" not in text:
        results.append(finding(record, "TF_NO_REQUIRED_VERSION", "Terraform file does not declare required_version", Severity.MEDIUM, None, None, "Declare a Terraform CLI version constraint in a terraform block."))
    if "terraform" in text and "backend" not in text and record.path.name in {"main.tf", "provider.tf"}:
        results.append(finding(record, "TF_NO_BACKEND_HINT", "Terraform configuration has no backend declaration", Severity.LOW, None, None, "Use a remote backend with locking for shared environments."))
    for idx, line in enumerate(record.lines, start=1):
        stripped = line.strip()
        if re.search(r"access_key\s*=|secret_key\s*=|client_secret\s*=", stripped):
            results.append(finding(record, "TF_INLINE_SECRET", "Terraform appears to contain inline credentials", Severity.CRITICAL, idx, stripped, "Move secrets to environment variables, Vault, SSM, or CI secret stores."))
    return results


def check_kubernetes_manifests(record: FileRecord) -> list[Finding]:
    if record.kind != "yaml":
        return []
    text = record.text
    if "apiVersion:" not in text or "kind:" not in text:
        return []
    results: list[Finding] = []
    kind_match = re.search(r"^kind:\s*(\w+)", text, flags=re.MULTILINE)
    kind = kind_match.group(1) if kind_match else "KubernetesObject"
    if kind in {"Deployment", "StatefulSet", "DaemonSet", "Pod"}:
        if "resources:" not in text:
            results.append(finding(record, "K8S_NO_RESOURCES", f"{kind} lacks resource requests/limits", Severity.HIGH, None, None, "Set CPU and memory requests and limits for every container."))
        if "readinessProbe:" not in text:
            results.append(finding(record, "K8S_NO_READINESS", f"{kind} lacks readinessProbe", Severity.MEDIUM, None, None, "Add readinessProbe so rollout and service routing reflect application health."))
        if "livenessProbe:" not in text:
            results.append(finding(record, "K8S_NO_LIVENESS", f"{kind} lacks livenessProbe", Severity.LOW, None, None, "Add livenessProbe only when the app can safely be restarted."))
    for idx, line in enumerate(record.lines, start=1):
        stripped = line.strip()
        if stripped.startswith("privileged:") and "true" in stripped.lower():
            results.append(finding(record, "K8S_PRIVILEGED", "Manifest enables privileged container", Severity.CRITICAL, idx, stripped, "Remove privileged mode or isolate it behind a documented exception."))
        if stripped.startswith("image:") and ":latest" in stripped.lower():
            results.append(finding(record, "K8S_LATEST_IMAGE", "Manifest uses latest image tag", Severity.MEDIUM, idx, stripped, "Pin workload images to versioned tags or digests."))
    return results


def check_jenkins_pipeline(record: FileRecord) -> list[Finding]:
    if record.kind != "jenkins":
        return []
    text = record.text
    results: list[Finding] = []
    if "pipeline" in text and "options" not in text:
        results.append(finding(record, "JENKINS_NO_OPTIONS", "Pipeline lacks global options", Severity.LOW, None, None, "Add timestamps, timeout, buildDiscarder, and disableConcurrentBuilds where appropriate."))
    if "withCredentials" not in text and re.search(r"password|token|secret", text, flags=re.IGNORECASE):
        results.append(finding(record, "JENKINS_SECRET_HANDLING", "Pipeline mentions secrets without withCredentials", Severity.HIGH, None, None, "Use Jenkins credentials binding instead of inline values."))
    if "junit" not in text.lower() and "test" in text.lower():
        results.append(finding(record, "JENKINS_NO_TEST_REPORTS", "Pipeline runs tests without publishing reports", Severity.LOW, None, None, "Publish JUnit or equivalent test reports as pipeline artifacts."))
    return results


def check_python_hardcoded_paths(record: FileRecord) -> list[Finding]:
    if record.kind != "python":
        return []
    results: list[Finding] = []
    unix_user_path = "/" + "home" + "/[^/]+"
    windows_user_path = re.escape("C:" + chr(92) + "Users" + chr(92))
    local_path_pattern = re.compile(unix_user_path + "|" + windows_user_path)
    for idx, line in enumerate(record.lines, start=1):
        stripped = line.strip()
        if local_path_pattern.search(stripped):
            results.append(finding(record, "PY_LOCAL_PATH", "Python code contains machine-local path", Severity.LOW, idx, stripped, "Use pathlib, environment variables, or CLI parameters for environment-specific paths."))
        if re.search(r"except\s*:", stripped):
            results.append(finding(record, "PY_BARE_EXCEPT", "Python code uses bare except", Severity.MEDIUM, idx, stripped, "Catch a specific exception or re-raise after logging context."))
    return results


def check_github_actions_workflow(record: FileRecord) -> list[Finding]:
    if record.kind != "yaml" or not record.relative_path.startswith(".github/workflows/"):
        return []
    results: list[Finding] = []
    text = record.text
    if "pull_request_target:" in text:
        results.append(finding(record, "GHA_PULL_REQUEST_TARGET", "Workflow uses pull_request_target", Severity.HIGH, None, None, "Use pull_request for untrusted code, or isolate pull_request_target workflows from checkout and script execution."))
    if "permissions:" not in text:
        results.append(finding(record, "GHA_NO_PERMISSIONS", "Workflow does not declare token permissions", Severity.MEDIUM, None, None, "Declare least-privilege GITHUB_TOKEN permissions at workflow or job level."))
    for idx, line in enumerate(record.lines, start=1):
        stripped = line.strip()
        if re.search(r"uses:\s*[^@\s]+$", stripped):
            results.append(finding(record, "GHA_UNPINNED_ACTION", "Workflow action is not pinned to a version", Severity.MEDIUM, idx, stripped, "Pin actions to a version tag or commit SHA."))
        if re.search(r"run:\s*curl .*?\|\s*(sudo\s+)?bash", stripped):
            results.append(finding(record, "GHA_CURL_BASH", "Workflow pipes downloaded content into bash", Severity.HIGH, idx, stripped, "Download, checksum, inspect, then execute external scripts."))
    return results


def check_iam_policy_json(record: FileRecord) -> list[Finding]:
    if record.kind != "json":
        return []
    if '"Statement"' not in record.text or '"Effect"' not in record.text:
        return []
    results: list[Finding] = []
    for idx, line in enumerate(record.lines, start=1):
        stripped = line.strip()
        if re.search(r'"Action"\s*:\s*"\*"', stripped):
            results.append(finding(record, "IAM_WILDCARD_ACTION", "IAM policy grants wildcard action", Severity.HIGH, idx, stripped, "Replace Action:* with a narrow action list required by the workload."))
        if re.search(r'"Resource"\s*:\s*"\*"', stripped):
            results.append(finding(record, "IAM_WILDCARD_RESOURCE", "IAM policy grants wildcard resource", Severity.MEDIUM, idx, stripped, "Scope Resource to exact ARNs where AWS service support allows it."))
        if re.search(r'"Effect"\s*:\s*"Allow"', stripped) and "NotAction" in record.text:
            results.append(finding(record, "IAM_ALLOW_NOTACTION", "IAM policy uses Allow with NotAction", Severity.HIGH, idx, stripped, "Avoid Allow+NotAction because it can grant broad unintended permissions."))
    return results


RULES: list[Rule] = [
    Rule("DOCKER_USER_ROOT", "Detect root containers", {"dockerfile"}, check_docker_root),
    Rule("DOCKER_PINNING", "Detect weak Docker pinning and package hygiene", {"dockerfile"}, check_docker_pin_versions),
    Rule("SHELL_SAFETY", "Detect risky shell automation", {"shell"}, check_shell_safety),
    Rule("TF_STATE_VERSION", "Detect Terraform state/version/secrets issues", {"terraform"}, check_terraform_state_and_version),
    Rule("K8S_WORKLOADS", "Detect Kubernetes workload production gaps", {"yaml"}, check_kubernetes_manifests),
    Rule("GITHUB_ACTIONS", "Detect GitHub Actions workflow risks", {"yaml"}, check_github_actions_workflow),
    Rule("IAM_POLICY", "Detect risky IAM policy grants", {"json"}, check_iam_policy_json),
    Rule("JENKINS_PIPELINE", "Detect Jenkins production gaps", {"jenkins"}, check_jenkins_pipeline),
    Rule("PYTHON_PORTABILITY", "Detect Python portability issues", {"python"}, check_python_hardcoded_paths),
]
