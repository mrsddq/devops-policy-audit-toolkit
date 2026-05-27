from devops_toolkit.metrics import compute_metrics, group_by_file, parent_bucket
from devops_toolkit.models import Finding, Severity


def f(rule, path, severity):
    return Finding(rule_id=rule, title=rule, path=path, severity=severity)


def test_parent_bucket_for_nested_and_root_files():
    assert parent_bucket("Dockerfile") == "."
    assert parent_bucket("k8s/deploy.yaml") == "k8s"


def test_compute_metrics_counts_rule_severity_and_directory():
    metrics = compute_metrics([
        f("A", "k8s/deploy.yaml", Severity.HIGH),
        f("A", "k8s/pod.yaml", Severity.LOW),
        f("B", "Dockerfile", Severity.CRITICAL),
    ])
    assert metrics.total == 3
    assert metrics.by_rule["A"] == 2
    assert metrics.by_directory["k8s"] == 2
    assert metrics.highest_severity == Severity.CRITICAL


def test_group_by_file_keeps_findings_per_path():
    findings = [f("A", "x", Severity.LOW), f("B", "x", Severity.HIGH)]
    assert len(group_by_file(findings)["x"]) == 2
