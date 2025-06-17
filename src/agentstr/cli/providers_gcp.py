"""GCP provider implementation extracted from providers.py."""
from __future__ import annotations

import subprocess
import shutil
import importlib
import os
from pathlib import Path
from typing import Dict, Optional, List

import click
import textwrap
import yaml  # type: ignore

from .providers import _catch_exceptions, register_provider, Provider  # type: ignore


@register_provider("gcp")
class GCPProvider(Provider):  # noqa: D401
    """Google Kubernetes Engine (GKE) implementation using gcloud & kubectl CLI commands."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__("gcp")
        self._lazy_import("google.cloud.run_v2", "google-cloud-run")

    # ------------------------------------------------------------------
    # Lazy import helper
    # ------------------------------------------------------------------
    def _lazy_import(self, module_name: str, pip_name: str):  # noqa: D401
        try:
            importlib.import_module(module_name)
        except ImportError:  # pragma: no cover
            click.echo(
                f"GCP provider requires {pip_name}. Install with 'pip install {pip_name}' to enable.",
                err=True,
            )
            raise

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _run_cmd(self, cmd: List[str]):  # noqa: D401
        """Run shell command and stream output, raises on failure."""
        click.echo(" ".join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert proc.stdout
        for line in proc.stdout:
            click.echo(line.rstrip())
        proc.wait()
        if proc.returncode != 0:
            raise click.ClickException(f"Command {' '.join(cmd)} failed with code {proc.returncode}")

    def _ensure_ar_repo(self, repo: str, project: str, region: str):  # noqa: D401
        """Ensure Artifact Registry repository exists, create if missing."""
        # First, make sure Artifact Registry API is enabled (idempotent)
        subprocess.run(
            [
                "gcloud",
                "services",
                "enable",
                "artifactregistry.googleapis.com",
                "--project",
                project,
                "--quiet",
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Check repo existence
        describe_cmd = [
            "gcloud",
            "artifacts",
            "repositories",
            "describe",
            repo,
            "--project",
            project,
            "--location",
            region,
            "--format",
            "value(name)",
        ]
        result = subprocess.run(describe_cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return  # exists
        click.echo(f"Creating Artifact Registry repository '{repo}' in {region} ...")
        create_cmd = [
            "gcloud",
            "artifacts",
            "repositories",
            "create",
            repo,
            "--repository-format=docker",
            "--project",
            project,
            "--location",
            region,
            "--description",
            "agentstr container images",
        ]
        self._run_cmd(create_cmd)

    def _check_prereqs(self):  # noqa: D401
        if not shutil.which("gcloud"):
            raise click.ClickException("gcloud CLI is required for GCP provider. Install Google Cloud SDK.")
        if not shutil.which("kubectl"):
            raise click.ClickException("kubectl is required for GKE provider. Install kubectl and ensure it is on PATH.")
        project = os.getenv("GCP_PROJECT")
        region = os.getenv("GCP_REGION", "us-central1")
        zone = os.getenv("GCP_ZONE", f"{region}-b")
        if not project:
            raise click.ClickException("GCP_PROJECT env var must be set to your GCP project ID.")
        return project, region, zone

    # ------------------------------------------------------------------
    # Image build/push
    # ------------------------------------------------------------------
    def _build_and_push_image(self, file_path: Path, deployment_name: str, dependencies: list[str]) -> str:  # noqa: D401
        import uuid
        import tempfile

        project, region, zone = self._check_prereqs()
        repo = "agentstr"
        # Ensure Artifact Registry repository exists
        self._ensure_ar_repo(repo, project, region)
        image_tag = uuid.uuid4().hex[:8]
        image_uri = f"{region}-docker.pkg.dev/{project}/{repo}/{deployment_name}:{image_tag}"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dockerfile = tmp_path / "Dockerfile"
            deps_line = " " + " ".join(dependencies) if dependencies else ""
            if "agentstr-sdk" not in deps_line:
                deps_line = "agentstr-sdk[all] " + deps_line
            dockerfile.write_text(
                f"""
FROM python:3.12-slim
WORKDIR /app
COPY app.py /app/app.py
RUN pip install --no-cache-dir {deps_line}
CMD [\"python\", \"/app/app.py\"]
"""
            )
            temp_app = tmp_path / "app.py"
            temp_app.write_text(file_path.read_text())
            self._run_cmd(["docker", "build", "-t", image_uri, tmp_dir])
            self._run_cmd(["gcloud", "auth", "configure-docker", f"{region}-docker.pkg.dev", "--quiet"])
            self._run_cmd(["docker", "push", image_uri])
        return image_uri

    # ------------------------------------------------------------------
    # Provider interface
    # ------------------------------------------------------------------
    @_catch_exceptions
    def _ensure_autoscaler(self, project: str, zone: str, cluster_name: str):  # noqa: D401
        """Ensure the default node pool has autoscaling 1-3 nodes enabled."""
        self._run_cmd([
            "gcloud",
            "container",
            "clusters",
            "update",
            cluster_name,
            "--enable-autoscaling",
            "--min-nodes",
            "1",
            "--max-nodes",
            "3",
            "--zone",
            zone,
            "--project",
            project,
            "--node-pool",
            "default-pool",
            "--quiet",
        ])

    def _ensure_cluster(self, project: str, zone: str):  # noqa: D401
        cluster_name = "agentstr-cluster"
        # Check if cluster exists
        cmd_describe = [
            "gcloud",
            "container",
            "clusters",
            "describe",
            cluster_name,
            "--zone",
            zone,
            "--project",
            project,
            "--format=value(name)",
        ]
        result = subprocess.run(cmd_describe, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            # Cluster exists – ensure autoscaling configured
            self._ensure_autoscaler(project, zone, cluster_name)
            return cluster_name
        click.echo("Creating GKE standard cluster (this may take several minutes) ...")
        create_cmd = [
            "gcloud",
            "container",
            "clusters",
            "create",
            cluster_name,
            "--num-nodes",
            "1",
            "--enable-autoscaling",
            "--min-nodes",
            "1",
            "--max-nodes",
            "3",
            "--machine-type",
            "e2-medium",
            "--zone",
            zone,
            "--project",
            project,
            "--quiet",
        ]
        self._run_cmd(create_cmd)
        # Enable autoscaler after creation (redundant but idempotent)
        self._ensure_autoscaler(project, zone, cluster_name)
        return cluster_name

    def _configure_kubectl(self, cluster_name: str, project: str, zone: str):  # noqa: D401
        self._run_cmd([
            "gcloud",
            "container",
            "clusters",
            "get-credentials",
            cluster_name,
            "--zone",
            zone,
            "--project",
            project,
        ])

    @_catch_exceptions
    def deploy(self, file_path: Path, deployment_name: str, *, secrets: Dict[str, str], **kwargs):  # noqa: D401
        deployment_name = deployment_name.replace("_", "-")
        env_vars = kwargs.get("env", {})
        dependencies = kwargs.get("dependencies", [])
        cpu = kwargs.get("cpu", 0.25)
        memory = int(kwargs.get("memory", 512))  # MiB
        click.echo(
            f"[GCP/GKE] Deploying {file_path} as '{deployment_name}' (cpu={cpu}, memory={memory}, deps={dependencies}) ..."
        )
        project, region, zone = self._check_prereqs()
        image_uri = self._build_and_push_image(file_path, deployment_name, dependencies)

        cluster_name = self._ensure_cluster(project, zone)
        self._configure_kubectl(cluster_name, project, zone)

        # Construct Kubernetes deployment & service manifests
        env_list = [{"name": k, "value": v} for k, v in {**env_vars, **secrets}.items()]
        deployment_yaml = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": deployment_name},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": deployment_name}},
                "template": {
                    "metadata": {"labels": {"app": deployment_name}},
                    "spec": {
                        "containers": [
                            {
                                "name": deployment_name,
                                "image": image_uri,
                                "ports": [{"containerPort": 80}],
                                "resources": {
                                    "requests": {"cpu": str(cpu), "memory": f"{memory}Mi"},
                                    "limits": {"cpu": str(cpu), "memory": f"{memory}Mi"},
                                },
                                "env": env_list,
                            }
                        ]
                    },
                },
            },
        }
        # Apply manifests via kubectl
        manifest = yaml.safe_dump_all([deployment_yaml])
        apply_cmd = ["kubectl", "apply", "-f", "-"]
        click.echo("Applying Kubernetes manifests ...")
        proc = subprocess.Popen(apply_cmd, stdin=subprocess.PIPE, text=True)
        assert proc.stdin is not None
        proc.stdin.write(manifest)
        proc.stdin.close()
        proc.wait()
        if proc.returncode != 0:
            raise click.ClickException("kubectl apply failed")
        click.echo("Deployment submitted. It may take a few minutes for deployment to start up.")

    @_catch_exceptions
    def list(self, *, name_filter: Optional[str] = None):  # noqa: D401
        """List GKE services with external IP."""
        project, region, zone = self._check_prereqs()
        self._run_cmd(["kubectl", "get", "deployments", "-o", "wide"])

    @_catch_exceptions
    def logs(self, deployment_name: str):  # noqa: D401
        deployment_name = deployment_name.replace("_", "-")
        self._run_cmd(["kubectl", "logs", f"deployment/{deployment_name}", "--tail", "100"])

    @_catch_exceptions
    def destroy(self, deployment_name: str):  # noqa: D401
        deployment_name = deployment_name.replace("_", "-")
        # Delete service and deployment
        self._run_cmd(["kubectl", "delete", "deployment", deployment_name, "--ignore-not-found=true"])
        click.echo("Service and deployment deleted.")
