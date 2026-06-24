# DevOps Validation Toolkit

[![CI](https://github.com/mrsddq/devops-policy-audit-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/mrsddq/devops-policy-audit-toolkit/actions/workflows/ci.yml)

A practical DevOps repository audit tool that scans Dockerfiles, Kubernetes YAML, Terraform, IAM policies, GitHub Actions workflows, Jenkins pipelines, shell automation, and Python helper scripts for production-readiness issues.

This repository contains a working Python package, CLI entry point, static analysis rules, tests, Docker support, CI workflow, and reference DevOps material.

## What it checks

- Docker: missing non-root user, latest tags, weak package-install hygiene
- Shell: missing strict mode, curl-pipe-bash, world-writable permissions
- Terraform: missing required version, missing backend hint, inline credentials
- Kubernetes: missing resources, missing probes, privileged containers, latest images
- IAM: wildcard actions/resources and risky `Allow` + `NotAction`
- GitHub Actions: missing token permissions, `pull_request_target`, unpinned actions, curl-pipe-bash
- Jenkins: missing options, weak credential handling, missing test reporting
- Python: local machine paths and bare exception handling

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m unittest discover -s tests
devops-audit . --config devops-audit.config.json --format markdown --output reports/audit.md --fail-on-high
```

Or use the project automation:

```bash
make install
make test
make audit
make reports
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
- HTML report renderer for stakeholder-friendly reviews
- SARIF report output for CI/code-scanning ingestion
- Versioned finding baselines for incremental adoption
- JSON/YAML policy configuration with severity gates and documented overrides
- Release checklist in `docs/RELEASE_CHECKLIST.md`

## Policy and Baselines

```bash
devops-audit . --config devops-audit.config.json --format sarif --output reports/audit.sarif
devops-audit . --config devops-audit.config.json --format html --output reports/audit.html
devops-audit . --write-baseline reports/baseline.json
devops-audit . --baseline reports/baseline.json --fail-on-high
```

The policy file controls severity gates, ignored paths, and documented rule overrides. Baselines are versioned JSON files that let an existing repository fail only on new findings while older exceptions are being remediated.
