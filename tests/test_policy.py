from devops_toolkit.models import Finding, Severity
from devops_toolkit.policy import AuditPolicy, PolicyOverride


def test_policy_filters_ignored_paths():
    policy = AuditPolicy(ignored_paths=("docs/*",))
    finding = Finding(rule_id="X", title="x", severity=Severity.HIGH, path="docs/readme.md")
    assert policy.filter_findings([finding]) == []


def test_policy_override_removes_matching_finding():
    policy = AuditPolicy(overrides=(PolicyOverride("K8S_NO_RESOURCES", "labs/*", "training lab"),))
    finding = Finding(rule_id="K8S_NO_RESOURCES", title="x", severity=Severity.HIGH, path="labs/pod.yaml")
    assert policy.is_overridden(finding)


def test_policy_fail_gate_uses_configured_severity():
    policy = AuditPolicy(fail_on=(Severity.CRITICAL,))
    high = Finding(rule_id="X", title="x", severity=Severity.HIGH, path="a")
    critical = Finding(rule_id="Y", title="y", severity=Severity.CRITICAL, path="b")
    assert not policy.should_fail([high])
    assert policy.should_fail([critical])
