"""GCP provider implementation extracted from providers.py."""
from __future__ import annotations

import subprocess
import shutil
import importlib
import os
from pathlib import Path
from typing import Dict, Optional, List

import click
import base64
import re
import yaml  # type: ignore
import uuid
import secrets
import tempfile

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

    # ------------------------------------------------------------------
    # Kubernetes manifest helper
    # ------------------------------------------------------------------
    def _apply_manifest(self, manifest_obj):  # noqa: D401
        """Apply a Kubernetes YAML manifest (dict or list) via kubectl."""
        # Accept single dict or list/iterator of docs
        if isinstance(manifest_obj, list):
            manifest_yaml = yaml.safe_dump_all(manifest_obj)
        else:
            manifest_yaml = yaml.safe_dump(manifest_obj)
        apply_cmd = ["kubectl", "apply", "-f", "-"]
        proc = subprocess.Popen(apply_cmd, stdin=subprocess.PIPE, text=True)
        assert proc.stdin is not None
        proc.stdin.write(manifest_yaml)
        proc.stdin.close()
        proc.wait()
        if proc.returncode != 0:
            raise click.ClickException("kubectl apply failed")

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

    # ------------------------------------------------------------------
    # Cluster node external IP helper
    # ------------------------------------------------------------------
    def _get_cluster_external_ips(self, cluster_name: str, project: str, zone: str) -> list[str]:  # noqa: D401
        """Return list of external IPv4 addresses of at most 5 GKE nodes."""
        list_cmd = [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--filter",
            f"name~^gke-{cluster_name}",
            "--project",
            project,
            "--zones",
            zone,
            "--format=value(networkInterfaces[0].accessConfigs[0].natIP)",
        ]
        try:
            output = subprocess.check_output(list_cmd, text=True).strip()
        except subprocess.CalledProcessError:
            return []
        ips = [line for line in output.split("\n") if line]
        return ips[:5]

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

    # ------------------------------------------------------------------
    # Private Service Connection helper for Cloud SQL private IP
    # ------------------------------------------------------------------
    def _ensure_private_vpc_connection(self, network: str, project: str):  # noqa: D401
        """Ensure VPC peering between network and Google managed services exists."""
        # Enable service networking API (idempotent)
        subprocess.run([
            "gcloud", "services", "enable", "servicenetworking.googleapis.com", "--project", project, "--quiet"
        ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Check existing peering
        peer_check = subprocess.run([
            "gcloud", "compute", "networks", "peerings", "list", "--network", network, "--project", project, "--format=value(name)"
        ], capture_output=True, text=True)
        if peer_check.returncode == 0 and peer_check.stdout.strip():
            return  # peering exists
        # Need to allocate IP range and connect peering (one-time)
        alloc_name = "google-managed-services-default"
        subprocess.run([
            "gcloud", "compute", "addresses", "create", alloc_name,
            "--global", "--purpose=VPC_PEERING", "--prefix-length=16",
            "--network", network, "--project", project, "--quiet"
        ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Connect peering with the allocated range
        subprocess.run([
            "gcloud", "services", "vpc-peerings", "connect",
            "--service=servicenetworking.googleapis.com",
            "--network", network,
            "--ranges", alloc_name,
            "--project", project,
            "--quiet",
        ], check=False)

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
        project, region, zone = self._check_prereqs()

        # ------------------------------------------------------------------
        # Workload Identity service account for Secret Manager access
        # ------------------------------------------------------------------
        gcp_sa_name = f"agentstr-{deployment_name}-sa"
        gcp_sa_email = f"{gcp_sa_name}@{project}.iam.gserviceaccount.com"
        # Ensure GCP service account exists
        sa_desc = subprocess.run([
            "gcloud", "iam", "service-accounts", "describe", gcp_sa_email, "--project", project, "--format=value(email)"],
            capture_output=True, text=True)
        if sa_desc.returncode != 0:
            click.echo(f"Creating GCP service account '{gcp_sa_email}' ...")
            self._run_cmd(["gcloud", "iam", "service-accounts", "create", gcp_sa_name, "--project", project])

        # Grant Secret Manager access scoped to each secret
        for secret_path in secrets.values():
            # Expect path like projects/{project}/secrets/{name}/versions/latest or similar
            parts = secret_path.split("/")
            if len(parts) < 4:
                click.echo(f"Skipping invalid secret reference '{secret_path}'", err=True)
                continue
            secret_name = parts[3]
            self._run_cmd([
                "gcloud", "secrets", "add-iam-policy-binding", secret_name,
                "--member", f"serviceAccount:{gcp_sa_email}",
                "--role", "roles/secretmanager.secretAccessor",
                "--project", project])

        project, region, zone = self._check_prereqs()
        image_uri = self._build_and_push_image(file_path, deployment_name, dependencies)

        cluster_name = self._ensure_cluster(project, zone)
        self._configure_kubectl(cluster_name, project, zone)
        # Using private IP connectivity – no need for authorized-networks patch.

        # Create/patch Kubernetes service account bound to GCP SA (Workload Identity)
        ksa_name = f"{deployment_name}-ksa"
        sa_yaml = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": ksa_name,
                "annotations": {
                    "iam.gke.io/gcp-service-account": gcp_sa_email
                }
            }
        }
        self._apply_manifest(sa_yaml)

        cpu = kwargs.get("cpu", 0.25)
        memory = int(kwargs.get("memory", 512))  # MiB
        click.echo(
            f"[GCP/GKE] Deploying {file_path} as '{deployment_name}' (cpu={cpu}, memory={memory}, deps={dependencies}) ..."
        )

        # ------------------------------------------------------------------
        # Materialize GCP Secret Manager secrets into Kubernetes secrets
        # ------------------------------------------------------------------
        secret_manifests: list[dict] = []
        env_list: list[dict] = [{"name": k, "value": v} for k, v in env_vars.items()]

        for env_name, secret_path in secrets.items():
            # Extract secret name from Resource path: projects/<proj>/secrets/<name>/versions/...
            parts = secret_path.split("/")
            if len(parts) < 4:
                click.echo(f"Skipping invalid secret reference '{secret_path}'", err=True)
                continue
            sm_name = parts[3]
            # Access secret value via gcloud CLI (latest version)
            result = subprocess.run([
                "gcloud",
                "secrets",
                "versions",
                "access",
                "latest",
                "--secret",
                sm_name,
                "--project",
                project,
            ], capture_output=True, text=True)
            if result.returncode != 0:
                click.echo(f"Failed to access secret '{sm_name}'", err=True)
                continue
            secret_val = result.stdout.strip()
            b64_val = base64.b64encode(secret_val.encode()).decode()
            # Kubernetes Secret metadata.name must match RFC1123 (lowercase alphanumerics and '-')
            def _sanitize(s: str) -> str:
                s = re.sub(r"[^a-z0-9-]+", "-", s.lower())
                s = re.sub(r"^-+", "", s)
                s = re.sub(r"-+$", "", s)
                return s[:253] or "secret"
            k8s_secret_name = _sanitize(f"{deployment_name}-{env_name}-secret")
            secret_manifest = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {"name": k8s_secret_name},
                "type": "Opaque",
                "data": {env_name: b64_val},
            }
            secret_manifests.append(secret_manifest)
            # reference via secretKeyRef
            env_list.append({
                "name": env_name,
                "valueFrom": {
                    "secretKeyRef": {
                        "name": k8s_secret_name,
                        "key": env_name,
                    }
                }
            })
        # ------------------------------------------------------------------
        # Build Deployment manifest
        # ------------------------------------------------------------------
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
                        "serviceAccountName": ksa_name,
                        "containers": [
                            {
                                "name": deployment_name,
                                "image": image_uri,
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
        # Delete previous deployment if it exists
        try:
            delete_cmd = ["kubectl", "delete", "deployment", deployment_name]
            self._run_cmd(delete_cmd)
        except Exception:
            pass
        # Apply manifests via kubectl – include secrets first
        manifest = yaml.safe_dump_all(secret_manifests + [deployment_yaml])
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
    def put_secret(self, name: str, value: str) -> str:  # noqa: D401
        import tempfile, textwrap as tw

        project, region, _zone = self._check_prereqs()
        # Ensure secret exists
        describe_cmd = [
            "gcloud",
            "secrets",
            "describe",
            name,
            "--project",
            project,
            "--format",
            "value(name)",
        ]
        result = subprocess.run(describe_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            self._run_cmd([
                "gcloud",
                "secrets",
                "create",
                name,
                "--replication-policy=automatic",
                "--project",
                project,
            ])
        # Add new version with value via temp file
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            tf.write(value)
            temp_path = tf.name
        self._run_cmd([
            "gcloud",
            "secrets",
            "versions",
            "add",
            name,
            "--data-file",
            temp_path,
            "--project",
            project,
        ])
        ref = f"projects/{project}/secrets/{name}/versions/latest"
        click.echo(f"Secret '{name}' stored in Secret Manager.")
        return ref

    @_catch_exceptions
    def provision_database(self, deployment_name: str) -> tuple[str, str]:  # noqa: D401
        """Provision a Cloud SQL Postgres instance and store DATABASE_URL secret."""
        project, region, zone = self._check_prereqs()

        instance_id = os.getenv('DATABASE_INSTANCE_ID', 'agentstr-db')
        root_pass = secrets.token_urlsafe(24)

        # ------------------------------------------------------------------
        # If DATABASE_URL secret already exists, assume DB is provisioned. Reuse.
        # ------------------------------------------------------------------
        secret_name = f"agentstrdb-DATABASE_URL"
        desc_pre = subprocess.run([
            "gcloud",
            "secrets",
            "describe",
            secret_name,
            "--project",
            project,
            "--format=value(name)",
        ], capture_output=True, text=True)
        if desc_pre.returncode == 0:
            click.echo("Cloud SQL instance & secret already exist – reusing.")
            secret_ref = f"projects/{project}/secrets/{secret_name}/versions/latest"
            return "DATABASE_URL", secret_ref
        # Check if instance exists
        inst_check = subprocess.run([
            "gcloud",
            "sql",
            "instances",
            "describe",
            instance_id,
            "--project",
            project,
            "--format=value(name)",
        ], capture_output=True, text=True)
        if inst_check.returncode != 0:
            click.echo("Creating Cloud SQL Postgres (db-f1-micro) – may take a few minutes ...")
            network = os.getenv("GCP_SQL_NETWORK", "default")
            # Ensure Private Service Connection between network and Google services exists
            self._ensure_private_vpc_connection(network, project)
            self._run_cmd([
                "gcloud",
                "sql",
                "instances",
                "create",
                instance_id,
                "--database-version=POSTGRES_15",
                "--cpu=1",
                "--memory=4GiB",
                "--region",
                region,
                "--network",
                network,
                "--no-assign-ip",  # private IP only
                "--project",
                project,
                "--quiet",
            ])
        # Wait until instance is RUNNABLE
        click.echo("Waiting for Cloud SQL instance to become RUNNABLE (this may take a few minutes) ...")
        import time
        while True:
            state_out = subprocess.check_output([
                "gcloud",
                "sql",
                "instances",
                "describe",
                instance_id,
                "--project",
                project,
                "--format=value(state)",
            ], text=True).strip()
            if state_out == "RUNNABLE":
                break
            time.sleep(10)

        # Set root password (idempotent)
        self._run_cmd([
            "gcloud",
            "sql",
            "users",
            "set-password",
            "postgres",
            "--instance",
            instance_id,
            "--password",
            root_pass,
            "--project",
            project,
        ])
        # Obtain private IP
        out = subprocess.check_output([
            "gcloud",
            "sql",
            "instances",
            "describe",
            instance_id,
            "--project",
            project,
            "--format=value(ipAddresses[0].ipAddress)",
        ], text=True)
        ip = out.strip()
        if not ip:
            raise click.ClickException("Cloud SQL instance lacks private IP; ensure Private Service Connection is configured.")
        conn = f"postgresql://postgres:{root_pass}@{ip}:5432/postgres"
        secret_name = secret_name
        # Check if secret exists already
        desc = subprocess.run([
            "gcloud",
            "secrets",
            "describe",
            secret_name,
            "--project",
            project,
            "--format=value(name)",
        ], capture_output=True, text=True)
        if desc.returncode == 0:
            click.echo("Reusing existing DATABASE_URL secret.")
            secret_ref = f"projects/{project}/secrets/{secret_name}/versions/latest"
            return "DATABASE_URL", secret_ref
        # Otherwise create
        secret_ref = self.put_secret(secret_name, conn)
        click.echo("Cloud SQL Postgres ready and secret stored.")
        return "DATABASE_URL", secret_ref

    def destroy(self, deployment_name: str):  # noqa: D401
        deployment_name = deployment_name.replace("_", "-")
        # Delete service and deployment
        self._run_cmd(["kubectl", "delete", "deployment", deployment_name, "--ignore-not-found=true"])
        click.echo("Service and deployment deleted.")
