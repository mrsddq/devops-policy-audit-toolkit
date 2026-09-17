# DevOps Policy Audit Toolkit runbook

Run these commands from the repository root with Python 3.10 or newer.

## Install and verify

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

The suite exercises audit rules, policy configuration, expiring overrides,
report formats, finding baselines, and repository traversal boundaries.

## Scan and review findings

```bash
devops-audit . --config devops-audit.config.json --format markdown --output reports/audit.md --fail-on-high
devops-audit . --config devops-audit.config.json --format sarif --output reports/audit.sarif
devops-audit . --config devops-audit.config.json --format html --output reports/audit.html
```

Review each finding against its source file. With `--fail-on-high`, status 2
indicates findings matching the policy's configured failure severities. Invalid
configuration, an invalid repository path, or invalid baseline data also exits with status
2 and a diagnostic on stderr; distinguish those errors from an audit result.
Without the failure flag, reported findings alone do not fail the command.

## Introduce an explicit baseline

After reviewing existing findings and deciding which to track separately:

```bash
devops-audit . --config devops-audit.config.json --write-baseline reports/baseline.json
devops-audit . --config devops-audit.config.json --baseline reports/baseline.json --fail-on-high
```

A baseline suppresses known findings; it does not fix them. Keep its reviewed
contents available to the CI job. If a command reads and writes the same baseline,
the current gate evaluates against the previous contents. Overrides require a
reason. An expiry date remains valid through that UTC date; expired overrides
stop suppressing findings.

## Container scan

```bash
docker build -t devops-validation-toolkit .
docker run --rm -v "$PWD:/repo:ro" devops-validation-toolkit /repo --format text
```

The read-only mount supports a stdout report. To write files inside a container,
provide a separate writable output mount rather than making the source writable.

## Scope and interpretation

The scanner uses static heuristics over repository files. It skips symbolic links
and prunes vendor/cache directories. It does not provision infrastructure, apply
remediation, validate Terraform providers, query a Kubernetes cluster, or prove
that a repository is secure. Use provider/schema validation and runtime checks
alongside findings. Reference DevOps material in this repository is distinct from
the executable `devops_toolkit` package.
