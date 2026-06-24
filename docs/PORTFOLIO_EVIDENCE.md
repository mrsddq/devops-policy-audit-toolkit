# Portfolio Evidence

This repo demonstrates a practical DevOps policy audit CLI with report output for engineering teams and CI.

## Verified Locally

```bash
python -m unittest discover -s tests
python -m devops_toolkit.cli . --config devops-audit.config.json --format markdown --output reports/audit-report.md
python -m devops_toolkit.cli . --config devops-audit.config.json --format html --output reports/audit-report.html
python -m devops_toolkit.cli . --config devops-audit.config.json --format sarif --output reports/audit-report.sarif
```

## Reviewer Evidence

| Evidence | Location | What it proves |
|---|---|---|
| CI badge | `README.md` | Tests and report generation run in GitHub Actions. |
| Rules engine | `devops_toolkit/rules.py` | Checks for Docker, Terraform, Kubernetes, IAM, GitHub Actions, Jenkins, shell and Python. |
| CLI | `devops_toolkit/cli.py` | Configurable scan root, output formats and fail gates. |
| Reports | `devops_toolkit/reporting.py` and `devops_toolkit/sarif.py` | JSON, Markdown, HTML and SARIF output. |
| Policy config | `devops-audit.config.json` | Severity gates, ignored paths and overrides. |
| Tests | `tests/` | Rule, CLI, reporting, policy and baseline coverage. |
