# DevOps

Serious DevOps learning and reference archive covering Linux, Git, Jenkins, Maven, Tomcat, Docker, Kubernetes, Terraform, AWS, and Azure.

This repository is intentionally an archive, but it now has a learning spine so the material reads as a coherent DevOps path instead of disconnected notes.

## Structure

```text
DevOps-AWS/       AWS, Jenkins, Terraform, Tomcat, YAML, and pipeline notes
DevOps-Azure/     Azure Terraform labs
Revision/         Docker and container revision examples
docs/
  roadmap.md
  labs-index.md
  command-checklist.md
  production-readiness.md
scripts/
  devops_audit.py
tests/
```

## Learning Path

1. Linux, Git, and shell fundamentals
2. CI with Jenkins
3. Java build and deployment with Maven and Tomcat
4. Docker images and containers
5. Kubernetes workloads and services
6. Terraform infrastructure as code
7. AWS and Azure deployment patterns
8. Monitoring, quality gates, and release discipline

## Recommended Portfolio Use

Keep this repository as a learning archive. For showcase work, extract polished labs into separate focused repos such as:

- `terraform-aws-webapp`
- `jenkins-tomcat-pipeline`
- `docker-kubernetes-labs`
- `azure-terraform-foundations`

## Repository Audit

```bash
python scripts/devops_audit.py --strict
python -m unittest discover -s tests
```

The audit checks that core DevOps artifacts are present and flags common repository hygiene issues such as unpinned Docker base images, missing Docker copy sources, and secret-like markers.
