# Production Readiness Checklist

Before a DevOps lab becomes portfolio-ready:

- No secrets, IPs, or passwords are committed.
- Infrastructure can be destroyed cleanly.
- Terraform state strategy is documented.
- IAM permissions are least privilege.
- Pipeline has build, test, scan, and deploy stages.
- Rollback strategy is documented.
- Logs and metrics are visible.
- Cost impact is understood.
- Cleanup commands are included.

## Audit Tool Operating Model

- Run the CLI in CI on every pull request.
- Publish Markdown, JSON, and SARIF reports as build artifacts.
- Fail pull requests on high and critical findings by default.
- Use a baseline only for legacy findings that already exist before adoption.
- Require every override to include a rule, path pattern, owner-readable reason, and review date.
- Keep generated reports and runtime caches out of source control.
