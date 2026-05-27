# DevOps Validation Toolkit

A practical DevOps repository audit tool that scans Dockerfiles, Kubernetes YAML, Terraform, Jenkins pipelines, shell automation, and Python helper scripts for production-readiness issues.

This repository contains a working Python package, CLI entry point, static analysis rules, tests, Docker support, CI workflow, and reference DevOps material.

## What it checks

- Docker: missing non-root user, latest tags, weak package-install hygiene
- Shell: missing strict mode, curl-pipe-bash, world-writable permissions
- Terraform: missing required version, missing backend hint, inline credentials
- Kubernetes: missing resources, missing probes, privileged containers, latest images
- Jenkins: missing options, weak credential handling, missing test reporting
- Python: local machine paths and bare exception handling

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
devops-audit . --format markdown --output reports/audit.md
```

## Docker

```bash
docker build -t devops-validation-toolkit .
docker run --rm -v "$PWD:/repo" devops-validation-toolkit /repo --format text
```

## Repository quality signals

- Real source package under `devops_toolkit/`
- Test suite under `tests/`
- CLI entry point through `pyproject.toml`
- GitHub Actions workflow
- Dockerfile for reproducible execution
- Markdown and JSON report renderers
