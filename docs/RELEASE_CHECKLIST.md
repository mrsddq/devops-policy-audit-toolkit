# Release Checklist

Use this checklist before presenting the toolkit as a polished DevOps portfolio project or tagging a release.

## Verification

```bash
python -m pip install -e .[dev]
pytest
devops-audit . --config devops-audit.config.json --format markdown --output reports/audit-report.md --fail-on-high
devops-audit . --config devops-audit.config.json --format sarif --output reports/audit-report.sarif
```

## Release Evidence

- [ ] CI run is green on the release commit.
- [ ] `reports/audit-report.md` is generated from the release commit.
- [ ] SARIF output is generated and attached as a CI artifact.
- [ ] README examples match the current CLI flags.
- [ ] `devops-audit.config.json` documents any ignored paths or accepted risks.
- [ ] Known limitations are listed in `docs/operational-runbook.md` or the README.

## Version Notes Template

```text
Version:
Date:
Scope:
Rules added:
Rules changed:
False-positive handling:
Breaking changes:
Verification commands:
```
