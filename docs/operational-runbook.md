# Operational Runbook

## Purpose

The DevOps validation toolkit gives repository owners a repeatable quality gate for infrastructure and delivery assets. It scans Dockerfiles, Terraform, Kubernetes YAML, Jenkins pipelines, shell scripts, and Python helpers before changes are merged.

## Standard Commands

```bash
make install
make test
make audit
make reports
```

## CI Gate

The default policy fails on high and critical findings. Teams can adopt the tool on an older repository by writing a baseline, reviewing the existing findings, and then failing only on new violations.

```bash
devops-audit . --write-baseline reports/baseline.json
devops-audit . --baseline reports/baseline.json --fail-on-high
```

## Release Checklist

- Tests pass with `python -m unittest discover -s tests`.
- Audit exits successfully with `--fail-on-high`.
- Markdown, JSON, and SARIF reports are generated.
- Generated reports remain untracked.
- Policy overrides include a reason and a path pattern.
- Docker image builds from the pinned root `Dockerfile`.

## Incident Response

If CI fails on a new finding:

1. Read the rule recommendation in the report.
2. Fix the underlying configuration or automation.
3. Add a policy override only when there is a documented business reason.
4. Re-run `make reports` and attach the updated output to the review.
