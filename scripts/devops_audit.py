import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = (
    re.compile(r"aws_access_key_id\s*=", re.IGNORECASE),
    re.compile(r"aws_secret_access_key\s*=", re.IGNORECASE),
    re.compile(r"-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----"),
    re.compile(r"(password|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}", re.IGNORECASE),
)
TEXT_EXTENSIONS = {".groovy", ".md", ".php", ".tf", ".txt", ".yaml", ".yml", ""}


@dataclass(frozen=True)
class AuditResult:
    terraform_files: int
    yaml_files: int
    groovy_files: int
    markdown_files: int
    dockerfiles: int
    warnings: tuple[str, ...]


def repository_files(root: Path = ROOT) -> list[Path]:
    ignored_parts = {".git", ".terraform", ".idea", ".vscode"}
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and not ignored_parts.intersection(path.relative_to(root).parts)
    ]


def count_by_suffix(files: list[Path], suffix: str) -> int:
    return sum(1 for path in files if path.suffix.lower() == suffix)


def find_dockerfiles(files: list[Path]) -> list[Path]:
    return [path for path in files if path.name == "Dockerfile"]


def audit_dockerfiles(dockerfiles: list[Path], root: Path = ROOT) -> list[str]:
    warnings = []
    for dockerfile in dockerfiles:
        text = dockerfile.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.upper().startswith("FROM ") and ":" not in stripped.split()[1]:
                warnings.append(f"{dockerfile.relative_to(root)} uses an unpinned base image")
            if stripped.upper().startswith("COPY "):
                parts = stripped.split()
                if len(parts) >= 3 and parts[1] != ".":
                    source = dockerfile.parent / parts[1]
                    if not source.exists():
                        warnings.append(f"{dockerfile.relative_to(root)} copies missing source {parts[1]}")
    return warnings


def scan_for_secret_markers(files: list[Path], root: Path = ROOT) -> list[str]:
    warnings = []
    for path in files:
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                warnings.append(f"possible secret marker in {path.relative_to(root)}")
                break
    return warnings


def run_audit(root: Path = ROOT) -> AuditResult:
    files = repository_files(root)
    dockerfiles = find_dockerfiles(files)
    warnings = [
        *audit_dockerfiles(dockerfiles, root),
        *scan_for_secret_markers(files, root),
    ]
    return AuditResult(
        terraform_files=count_by_suffix(files, ".tf"),
        yaml_files=count_by_suffix(files, ".yaml") + count_by_suffix(files, ".yml"),
        groovy_files=count_by_suffix(files, ".groovy"),
        markdown_files=count_by_suffix(files, ".md"),
        dockerfiles=len(dockerfiles),
        warnings=tuple(warnings),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit DevOps repository structure and risky markers.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when warnings are found.")
    args = parser.parse_args()

    result = run_audit()
    print(f"Terraform files: {result.terraform_files}")
    print(f"YAML files: {result.yaml_files}")
    print(f"Groovy pipeline files: {result.groovy_files}")
    print(f"Markdown docs: {result.markdown_files}")
    print(f"Dockerfiles: {result.dockerfiles}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
        return 1 if args.strict else 0

    print("Audit passed with no warnings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
