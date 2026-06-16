from pathlib import Path
from devops_toolkit.inventory import build_inventory, classify_file


def test_classify_common_devops_files():
    assert classify_file(Path("Dockerfile")) == "dockerfile"
    assert classify_file(Path("Jenkinsfile")) == "jenkins"
    assert classify_file(Path("main.tf")) == "terraform"
    assert classify_file(Path("deployment.yaml")) == "yaml"


def test_inventory_reads_text_files(tmp_path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"not text")
    records = build_inventory(tmp_path)
    assert len(records) == 1
    assert records[0].kind == "dockerfile"


def test_inventory_ignores_vendor_directories(tmp_path):
    vendor = tmp_path / "node_modules" / "package"
    vendor.mkdir(parents=True)
    (vendor / "Dockerfile").write_text("FROM busybox:latest\n", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")

    records = build_inventory(tmp_path)

    assert len(records) == 1
    assert records[0].relative_path == "Dockerfile"
