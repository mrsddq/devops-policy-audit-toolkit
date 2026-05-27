from __future__ import annotations

from pathlib import Path
from .models import FileRecord, normalize_path

TEXT_EXTENSIONS = {
    ".py", ".sh", ".bash", ".zsh", ".tf", ".tfvars", ".yaml", ".yml", ".json",
    ".groovy", ".jenkinsfile", ".dockerfile", ".txt", ".md", ".ini", ".cfg", ".conf",
}
IGNORED_DIRS = {".git", ".pytest_cache", "__pycache__", ".venv", "venv", "node_modules", "dist", "build"}


def classify_file(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if name in {"dockerfile", "dockerfile.prod"} or suffix == ".dockerfile":
        return "dockerfile"
    if name in {"jenkinsfile", "jenkinsfile.groovy"} or suffix == ".groovy":
        return "jenkins"
    if suffix in {".tf", ".tfvars"}:
        return "terraform"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".sh":
        return "shell"
    if suffix == ".py":
        return "python"
    return "text"


def is_text_candidate(path: Path) -> bool:
    name = path.name.lower()
    suffix = path.suffix.lower()
    return name in {"dockerfile", "jenkinsfile", "makefile"} or suffix in TEXT_EXTENSIONS


def iter_source_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if is_text_candidate(path):
            paths.append(path)
    return sorted(paths)


def read_file(path: Path, root: Path) -> FileRecord | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding="latin-1")
        except Exception:
            return None
    except OSError:
        return None
    return FileRecord(path=path, relative_path=normalize_path(path, root), kind=classify_file(path), text=text)


def build_inventory(root: str | Path) -> list[FileRecord]:
    base = Path(root).resolve()
    records: list[FileRecord] = []
    for path in iter_source_files(base):
        record = read_file(path, base)
        if record is not None:
            records.append(record)
    return records


def build_legacy_inventory(root: str | Path):
    from .models import FileInventory
    base = Path(root).resolve()
    tf=[]; yaml=[]; groovy=[]; md=[]; docker=[]; other=[]
    for p in iter_source_files(base):
        kind=classify_file(p)
        if kind=='terraform': tf.append(p)
        elif kind=='yaml': yaml.append(p)
        elif kind=='jenkins': groovy.append(p)
        elif p.suffix.lower()=='.md': md.append(p)
        elif kind=='dockerfile': docker.append(p)
        else: other.append(p)
    return FileInventory(tuple(tf), tuple(yaml), tuple(groovy), tuple(md), tuple(docker), tuple(other))
