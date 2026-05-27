# Policy Model

The policy layer keeps audit behavior stable across local runs and CI.

## Severity Gates

`fail_on` defines which severities fail the command when `--fail-on-high` is enabled.

```json
{
  "policy": {
    "fail_on": ["high", "critical"]
  }
}
```

## Ignored Paths

Ignored paths remove files that are not source material, such as generated reports or tool caches.

```json
{
  "policy": {
    "ignored_paths": ["reports/*", ".terraform/*"]
  }
}
```

## Overrides

Overrides suppress a specific rule for a specific path pattern. They are meant for documented exceptions, not broad silencing.

```json
{
  "rule_id": "K8S_NO_LIVENESS",
  "path_pattern": "platform/jobs/*",
  "reason": "Batch jobs terminate naturally and should not be restarted by a liveness probe",
  "expires": "2026-12-31"
}
```

## Baselines

Baselines store deterministic finding fingerprints. They are useful when adopting the tool in a repository that already has known issues.

```bash
devops-audit . --write-baseline reports/baseline.json
devops-audit . --baseline reports/baseline.json --fail-on-high
```
