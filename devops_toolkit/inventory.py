from pathlib import Path

from .models import FileInventory


IGNORED_PARTS = {
    ".git",
    ".idea",
    ".pytest_cache",
    ".terraform",
    ".vscode",
    "__pycache__",
}


def repository_files(root: Path) -> tuple[Path, ...]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if IGNORED_PARTS.intersection(relative_parts):
            continue
        files.append(path)
    return tuple(sorted(files))


def build_inventory(root: Path) -> FileInventory:
    terraform_files = []
    yaml_files = []
    groovy_files = []
    markdown_files = []
    dockerfiles = []
    other_files = []

    for path in repository_files(root):
        suffix = path.suffix.lower()
        if path.name == "Dockerfile":
            dockerfiles.append(path)
        elif suffix == ".tf":
            terraform_files.append(path)
        elif suffix in {".yaml", ".yml"}:
            yaml_files.append(path)
        elif suffix == ".groovy":
            groovy_files.append(path)
        elif suffix == ".md":
            markdown_files.append(path)
        else:
            other_files.append(path)

    return FileInventory(
        terraform_files=tuple(terraform_files),
        yaml_files=tuple(yaml_files),
        groovy_files=tuple(groovy_files),
        markdown_files=tuple(markdown_files),
        dockerfiles=tuple(dockerfiles),
        other_files=tuple(other_files),
    )

