import re
from pathlib import Path

from .models import Finding, FileInventory


SECRET_PATTERNS = (
    re.compile(r"aws_access_key_id\s*=", re.IGNORECASE),
    re.compile(r"aws_secret_access_key\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----"),
    re.compile(r"(password|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}", re.IGNORECASE),
)
TEXT_EXTENSIONS = {".groovy", ".md", ".php", ".tf", ".txt", ".yaml", ".yml", ""}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def check_secret_markers(files: tuple[Path, ...]) -> list[Finding]:
    findings = []
    for path in files:
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = read_text(path)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(Finding("secret-marker", path, "possible credential-like value"))
                break
    return findings


def check_dockerfiles(dockerfiles: tuple[Path, ...]) -> list[Finding]:
    findings = []
    for dockerfile in dockerfiles:
        text = read_text(dockerfile)
        has_cmd_or_entrypoint = False
        for line in text.splitlines():
            stripped = line.strip()
            upper = stripped.upper()
            if not stripped or stripped.startswith("#"):
                continue
            if upper.startswith("FROM "):
                image = stripped.split()[1]
                if ":" not in image and "@" not in image:
                    findings.append(Finding("docker-base-pin", dockerfile, "base image is not pinned"))
            if upper.startswith("COPY "):
                parts = stripped.split()
                if len(parts) >= 3 and parts[1] != ".":
                    source = dockerfile.parent / parts[1]
                    if not source.exists():
                        findings.append(Finding("docker-copy-source", dockerfile, f"missing COPY source {parts[1]}"))
            if upper.startswith("CMD ") or upper.startswith("ENTRYPOINT "):
                has_cmd_or_entrypoint = True
        if not has_cmd_or_entrypoint:
            findings.append(Finding("docker-runtime", dockerfile, "Dockerfile has no CMD or ENTRYPOINT"))
    return findings


def check_terraform(files: tuple[Path, ...]) -> list[Finding]:
    findings = []
    for path in files:
        text = read_text(path)
        if 'provider "aws"' in text and "region" not in text:
            findings.append(Finding("terraform-provider-region", path, "AWS provider has no visible region"))
        if "resource " in text and "tags" not in text:
            findings.append(Finding("terraform-tags", path, "resource file has no tags block", severity="info"))
    return findings


def check_kubernetes_yaml(files: tuple[Path, ...]) -> list[Finding]:
    findings = []
    for path in files:
        text = read_text(path)
        if "apiVersion:" not in text and "kind:" not in text:
            continue
        if "apiVersion:" not in text:
            findings.append(Finding("kubernetes-api-version", path, "manifest has no apiVersion"))
        if "kind:" not in text:
            findings.append(Finding("kubernetes-kind", path, "manifest has no kind"))
        if "image:" in text and ":latest" in text:
            findings.append(Finding("kubernetes-image-pin", path, "manifest uses a latest image tag"))
    return findings


def check_jenkins(files: tuple[Path, ...]) -> list[Finding]:
    findings = []
    for path in files:
        text = read_text(path)
        if "pipeline" in text and "stages" not in text:
            findings.append(Finding("jenkins-stages", path, "pipeline has no stages block"))
        if "credentials" in text.lower() and "environment" in text.lower():
            findings.append(Finding("jenkins-credentials", path, "review credential handling", severity="info"))
    return findings


def run_all_checks(inventory: FileInventory) -> list[Finding]:
    files = (
        inventory.terraform_files
        + inventory.yaml_files
        + inventory.groovy_files
        + inventory.markdown_files
        + inventory.dockerfiles
        + inventory.other_files
    )
    return [
        *check_dockerfiles(inventory.dockerfiles),
        *check_secret_markers(files),
        *check_terraform(inventory.terraform_files),
        *check_kubernetes_yaml(inventory.yaml_files),
        *check_jenkins(inventory.groovy_files),
    ]

