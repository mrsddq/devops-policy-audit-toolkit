from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    check: str
    path: Path
    message: str
    severity: str = "warning"

    def format(self, root: Path) -> str:
        return f"[{self.severity}] {self.check}: {self.path.relative_to(root)} - {self.message}"


@dataclass(frozen=True)
class FileInventory:
    terraform_files: tuple[Path, ...] = ()
    yaml_files: tuple[Path, ...] = ()
    groovy_files: tuple[Path, ...] = ()
    markdown_files: tuple[Path, ...] = ()
    dockerfiles: tuple[Path, ...] = ()
    other_files: tuple[Path, ...] = ()

    @property
    def total_files(self) -> int:
        return (
            len(self.terraform_files)
            + len(self.yaml_files)
            + len(self.groovy_files)
            + len(self.markdown_files)
            + len(self.dockerfiles)
            + len(self.other_files)
        )


@dataclass
class AuditReport:
    root: Path
    inventory: FileInventory
    findings: list[Finding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(finding.severity in {"error", "warning"} for finding in self.findings)

    def summary_lines(self) -> list[str]:
        return [
            f"Terraform files: {len(self.inventory.terraform_files)}",
            f"YAML files: {len(self.inventory.yaml_files)}",
            f"Groovy pipeline files: {len(self.inventory.groovy_files)}",
            f"Markdown docs: {len(self.inventory.markdown_files)}",
            f"Dockerfiles: {len(self.inventory.dockerfiles)}",
            f"Total scanned files: {self.inventory.total_files}",
        ]

