"""Azure provider stub implementation extracted from providers.py."""
from __future__ import annotations

import importlib
import subprocess
import shutil
import os
import uuid
import tempfile
from pathlib import Path
from typing import Dict, Optional, List

import click

from .providers import _catch_exceptions, register_provider, Provider  # type: ignore


@register_provider("azure")
class AzureProvider(Provider):  # noqa: D401
    """Azure Container Instances implementation using az CLI and Docker."""

    REGISTRY_NAME = "agentstr"
    IMAGE_TAG_BYTES = 8

    def __init__(self) -> None:  # noqa: D401
        super().__init__("azure")
        # Ensure required SDKs are installed (not strictly needed when az CLI is used but helpful)
        self._lazy_import("azure.mgmt.containerinstance", "azure-mgmt-containerinstance")
        self._lazy_import("azure.identity", "azure-identity")

    # ------------------------------------------------------------------
    # Lazy import helper
    # ------------------------------------------------------------------
    def _lazy_import(self, module_name: str, pip_name: str):  # noqa: D401
        try:
            importlib.import_module(module_name)
        except ImportError:  # pragma: no cover
            click.echo(
                f"Azure provider requires {pip_name}. Install with 'pip install {pip_name}' to enable.",
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

    def _check_prereqs(self):  # noqa: D401
        if not shutil.which("az"):
            raise click.ClickException("Azure CLI ('az') is required for Azure provider. Install it and login via 'az login'.")
        if not shutil.which("docker"):
            raise click.ClickException("Docker is required to build container images.")
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        region = os.getenv("AZURE_REGION", "eastus")
        resource_group = os.getenv("AZURE_RESOURCE_GROUP", "agentstr-rg")
        if not subscription_id:
            raise click.ClickException("AZURE_SUBSCRIPTION_ID environment variable must be set.")
        return subscription_id, region, resource_group

    def _ensure_resource_group(self, resource_group: str, region: str):  # noqa: D401
        show_cmd = [
            "az",
            "group",
            "show",
            "--name",
            resource_group,
            "--query",
            "name",
            "-o",
            "tsv",
        ]
        result = subprocess.run(show_cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return  # exists
        click.echo(f"Creating resource group '{resource_group}' in {region} ...")
        self._run_cmd(["az", "group", "create", "--name", resource_group, "--location", region])

    def _ensure_acr(self, resource_group: str, region: str) -> str:  # noqa: D401
        login_server_cmd = [
            "az",
            "acr",
            "show",
            "--name",
            self.REGISTRY_NAME,
            "--resource-group",
            resource_group,
            "--query",
            "loginServer",
            "-o",
            "tsv",
        ]
        result = subprocess.run(login_server_cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        click.echo(f"Creating Azure Container Registry '{self.REGISTRY_NAME}' ...")
        self._run_cmd(
            [
                "az",
                "acr",
                "create",
                "--name",
                self.REGISTRY_NAME,
                "--resource-group",
                resource_group,
                "--sku",
                "Basic",
                "--location",
                region,
                "--admin-enabled",
                "true",
            ]
        )
        # Retrieve login server again
        result = subprocess.run(login_server_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise click.ClickException("Failed to retrieve ACR login server after creation.")
        return result.stdout.strip()

    def _build_and_push_image(
        self,
        file_path: Path,
        deployment_name: str,
        dependencies: list[str],
        login_server: str,
    ) -> str:  # noqa: D401
        tag = uuid.uuid4().hex[: self.IMAGE_TAG_BYTES]
        image_uri = f"{login_server}/{deployment_name}:{tag}"
        with tempfile.TemporaryDirectory() as tmp_dir:
            dockerfile_path = Path(tmp_dir) / "Dockerfile"
            deps_line = " " + " ".join(dependencies) if dependencies else ""
            if "agentstr-sdk" not in deps_line:
                deps_line = "agentstr-sdk[all] " + deps_line
            dockerfile_path.write_text(
                f"""
FROM mcr.microsoft.com/devcontainers/python:3.12
WORKDIR /app
COPY app.py /app/app.py
RUN pip install --no-cache-dir {deps_line}
CMD [\"python\", \"/app/app.py\"]
"""
            )
            temp_app = Path(tmp_dir) / "app.py"
            temp_app.write_text(file_path.read_text())
            self._run_cmd(["az", "acr", "login", "--name", self.REGISTRY_NAME])
            self._run_cmd(["docker", "build", "-t", image_uri, tmp_dir])
            self._run_cmd(["docker", "push", image_uri])
        return image_uri

    # ------------------------------------------------------------------
    # Provider interface
    # ------------------------------------------------------------------
    @_catch_exceptions
    def deploy(self, file_path: Path, deployment_name: str, *, secrets: Dict[str, str], **kwargs):  # noqa: D401
        deployment_name = deployment_name.replace("_", "-")
        env_vars = kwargs.get("env", {})
        dependencies = kwargs.get("dependencies", [])
        cpu = kwargs.get("cpu", 0.25)
        memory = int(kwargs.get("memory", 512))
        click.echo(
            f"[Azure/ACI] Deploying {file_path} as '{deployment_name}' (cpu={cpu}, memory={memory}, deps={dependencies}) ..."
        )
        _, region, resource_group = self._check_prereqs()
        self._ensure_resource_group(resource_group, region)
        login_server = self._ensure_acr(resource_group, region)
        image_uri = self._build_and_push_image(file_path, deployment_name, dependencies, login_server)

        env_cli_args: List[str] = []
        for k, v in {**env_vars, **secrets}.items():
            env_cli_args.extend(["--environment-variables", f"{k}={v}"])

        create_cmd = [
            "az",
            "container",
            "create",
            "--resource-group",
            resource_group,
            "--name",
            deployment_name,
            "--image",
            image_uri,
            "--cpu",
            str(cpu),
            "--memory",
            str(memory),
            "--restart-policy",
            "OnFailure",
            "--ports",
            "80",
        ] + env_cli_args
        self._run_cmd(create_cmd)
        click.echo("Deployment submitted. Use `agentstr logs` to view logs.")

    @_catch_exceptions
    def list(self, *, name_filter: Optional[str] = None):  # noqa: D401
        _, _, resource_group = self._check_prereqs()
        self._run_cmd(["az", "container", "list", "--resource-group", resource_group, "-o", "table"])

    @_catch_exceptions
    def logs(self, deployment_name: str):  # noqa: D401
        deployment_name = deployment_name.replace("_", "-")
        _, _, resource_group = self._check_prereqs()
        self._run_cmd(
            [
                "az",
                "container",
                "logs",
                "--resource-group",
                resource_group,
                "--name",
                deployment_name,
                "--tail",
                "100",
            ]
        )

    @_catch_exceptions
    def destroy(self, deployment_name: str):  # noqa: D401
        deployment_name = deployment_name.replace("_", "-")
        _, _, resource_group = self._check_prereqs()
        click.echo(f"[Azure/ACI] Deleting deployment '{deployment_name}' ...")
        self._run_cmd(
            [
                "az",
                "container",
                "delete",
                "--resource-group",
                resource_group,
                "--name",
                deployment_name,
                "--yes",
            ]
        )
        click.echo("Deployment deleted.")
