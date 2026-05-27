import tempfile
import unittest
from pathlib import Path

from devops_toolkit.checks import check_jenkins, check_kubernetes_yaml, check_secret_markers, check_terraform


class DevOpsCheckTests(unittest.TestCase):
    def test_secret_marker_detection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "inventory.txt"
            path.write_text("token: abcdefghijklmnopqrstuvwxyz\n", encoding="utf-8")

            findings = check_secret_markers((path,))

        self.assertEqual(findings[0].check, "secret-marker")

    def test_kubernetes_latest_image_detection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "deployment.yaml"
            path.write_text(
                "apiVersion: apps/v1\nkind: Deployment\nimage: nginx:latest\n",
                encoding="utf-8",
            )

            findings = check_kubernetes_yaml((path,))

        self.assertEqual(findings[0].check, "kubernetes-image-pin")

    def test_terraform_provider_region_detection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "provider.tf"
            path.write_text('provider "aws" {}\n', encoding="utf-8")

            findings = check_terraform((path,))

        self.assertEqual(findings[0].check, "terraform-provider-region")

    def test_jenkins_pipeline_stage_detection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "Jenkinsfile.groovy"
            path.write_text("pipeline { agent any }\n", encoding="utf-8")

            findings = check_jenkins((path,))

        self.assertEqual(findings[0].check, "jenkins-stages")


if __name__ == "__main__":
    unittest.main()
