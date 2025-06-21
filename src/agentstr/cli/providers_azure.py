"""Azure provider stub implementation extracted from providers.py."""
from __future__ import annotations

import importlib
import json
import subprocess
import shutil
import os
import uuid
import secrets
import tempfile
from pathlib import Path
from typing import Dict, Optional, List, Set

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

    def _ensure_log_workspace(self, resource_group: str, region: str):  # noqa: D401
        """Ensure a Log Analytics workspace exists and return (workspace_id, key)."""

        workspace_name = "agentstr-logs"
        # Check exists
        try:
            out = subprocess.check_output([
                "az", "monitor", "log-analytics", "workspace", "show",
                "--resource-group", resource_group,
                "--workspace-name", workspace_name,
                "-o", "json"], text=True)
            ws = json.loads(out)
        except subprocess.CalledProcessError:
            click.echo(f"Creating Log Analytics workspace '{workspace_name}' ...")
            out = subprocess.check_output([
                "az", "monitor", "log-analytics", "workspace", "create",
                "--resource-group", resource_group,
                "--workspace-name", workspace_name,
                "--location", region,
                "-o", "json"], text=True)
            ws = json.loads(out)
        # Azure Container Instances expects the Workspace *ID* (a GUID), not the full
        # Azure resource ID path. The GUID is returned in the `customerId` field.
        ws_id = ws["customerId"]
        key_json = subprocess.check_output([
            "az", "monitor", "log-analytics", "workspace", "get-shared-keys",
            "--resource-group", resource_group,
            "--workspace-name", workspace_name,
            "-o", "json"], text=True)
        ws_key = json.loads(key_json)["primarySharedKey"]
        return ws_id, ws_key

    def _ensure_identity(self, resource_group: str, region: str, identity_name: str):  # noqa: D401
        """Ensure a user-assigned managed identity exists and return its resource ID and principalId."""
        show_cmd = [
            "az",
            "identity",
            "show",
            "--name",
            identity_name,
            "--resource-group",
            resource_group,
            "-o",
            "json",
        ]
        res = subprocess.run(show_cmd, capture_output=True, text=True)
        if res.returncode == 0:
            data = json.loads(res.stdout)
        else:
            click.echo(f"Creating managed identity '{identity_name}' ...")
            out = subprocess.check_output([
                "az",
                "identity",
                "create",
                "--name",
                identity_name,
                "--resource-group",
                resource_group,
                "--location",
                region,
                "-o",
                "json",
            ], text=True)
            data = json.loads(out)
        return data["id"], data["principalId"]

    def _check_prereqs(self):  # noqa: D401
        if not shutil.which("az"):
            raise click.ClickException("Azure CLI ('az') is required for Azure provider. Install it and login via 'az login'.")
        if not shutil.which("docker"):
            raise click.ClickException("Docker is required to build container images.")
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        region = os.getenv("AZURE_REGION", "westus2")
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

    def _docker_login_acr(self, login_server: str):  # noqa: D401
        """Login to ACR using admin credentials or env-vars, avoiding interactive prompt."""
        env_user = os.getenv("AZURE_ACR_USERNAME")
        env_pass = os.getenv("AZURE_ACR_PASSWORD")
        if env_user and env_pass:
            self._run_cmd(["docker", "login", "-u", env_user, "-p", env_pass, login_server])
            return

        cred_json = subprocess.check_output(["az", "acr", "credential", "show", "--name", self.REGISTRY_NAME, "-o", "json"], text=True)
        cred = json.loads(cred_json)
        username = cred["username"]
        password = cred["passwords"][0]["value"]
        self._run_cmd(["docker", "login", "-u", username, "-p", password, login_server])

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
            # Ensure Docker is authenticated with ACR (non-interactive)
            self._docker_login_acr(login_server)
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
        import math
        cpu_raw = kwargs.get("cpu", 0.25)
        # Azure ACI requires integer CPU cores (1-4). Round up if fractional.
        cpu_val = max(1, math.ceil(float(cpu_raw)))
        memory_mib = int(kwargs.get("memory", 512))
        # Azure CLI expects memory in GB (float). Convert if value looks like MiB.
        if memory_mib > 16:  # heuristic: values greater than 16 are likely MiB
            memory_gb = round(memory_mib / 1024, 2)
        else:
            memory_gb = memory_mib  # already GB

        click.echo(
            f"[Azure/ACI] Deploying {file_path} as '{deployment_name}' (cpu={cpu_val}, memory={memory_gb}GB, deps={dependencies}) ..."
        )
        _, region, resource_group = self._check_prereqs()
        self._ensure_resource_group(resource_group, region)
        login_server = self._ensure_acr(resource_group, region)
        # Ensure log workspace
        workspace_id, workspace_key = self._ensure_log_workspace(resource_group, region)
        image_uri = self._build_and_push_image(file_path, deployment_name, dependencies, login_server)

        # ------------------------------------------------------------------
        # Managed Identity & Key Vault access
        # ------------------------------------------------------------------
        identity_name = f"agentstr-{deployment_name}-id".replace("_", "-")
        identity_id, principal_id = self._ensure_identity(resource_group, region, identity_name)

        # Prepare environment + secret args following ACI syntax:
        # Build CLI args for plain environment variables
        env_pairs: List[str] = [f"{k}={v}" for k, v in env_vars.items()]
        env_cli_args: List[str] = ["--environment-variables"] + env_pairs if env_pairs else []

        # Secure environment variables containing actual secret values fetched from Key Vault
        secure_pairs: List[str] = []
        for k, uri in secrets.items():
            try:
                secret_val = subprocess.check_output([
                    "az",
                    "keyvault",
                    "secret",
                    "show",
                    "--id",
                    uri,
                    "--query",
                    "value",
                    "-o",
                    "tsv",
                ], text=True).strip()
            except subprocess.CalledProcessError as exc:  # pragma: no cover
                raise click.ClickException(f"Failed to fetch Key Vault secret '{uri}': {exc}") from exc
            secure_pairs.append(f"{k}={secret_val}")
        secure_cli_args: List[str] = ["--secure-environment-variables"] + secure_pairs if secure_pairs else []
        log_args: List[str] = ["--log-analytics-workspace", workspace_id, "--log-analytics-workspace-key", workspace_key]

        # Retrieve registry credentials (reuse docker login helper)
        env_user = os.getenv("AZURE_ACR_USERNAME")
        env_pass = os.getenv("AZURE_ACR_PASSWORD")
        if not (env_user and env_pass):
            cred_json = subprocess.check_output([
                "az",
                "acr",
                "credential",
                "show",
                "--name",
                self.REGISTRY_NAME,
                "-o",
                "json",
            ], text=True)
            cred_data = json.loads(cred_json)
            env_user = cred_data["username"]
            env_pass = cred_data["passwords"][0]["value"]

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
            str(cpu_val),
            "--memory",
            str(memory_gb),
            "--restart-policy",
            "OnFailure",
            "--os-type",
            "Linux",
            "--registry-login-server",
            login_server,
            "--registry-username",
            env_user,
            "--registry-password",
            env_pass,
            "--assign-identity",
            identity_id,
        ] + env_cli_args + secure_cli_args + log_args

        self._run_cmd(create_cmd)
        click.echo("Deployment submitted. Use `agentstr logs` to view logs.")

    @_catch_exceptions
    def list(self, *, name_filter: Optional[str] = None):  # noqa: D401
        _, _, resource_group = self._check_prereqs()
        self._run_cmd(["az", "container", "list", "--resource-group", resource_group, "-o", "table"])

    @_catch_exceptions
    def logs(self, deployment_name: str):  # noqa: D401
        """Stream logs for each container in the ACI container group; fall back to events if empty."""
        deployment_name = deployment_name.replace("_", "-")
        _, region, resource_group = self._check_prereqs()

        # First, try direct container logs command
        click.echo("Fetching container logs ...")
        try:
            self._run_cmd([
                "az",
                "container",
                "logs",
                "--resource-group",
                resource_group,
                "--name",
                deployment_name,
            ])
            return  # success
        except click.ClickException:
            click.echo("Container logs command failed, falling back to Log Analytics ...")

        # ------------------------------------------------------------------
        # Fall back: query Log Analytics workspace
        # ------------------------------------------------------------------
        try:
            ws_id, _ws_key = self._ensure_log_workspace(resource_group, region)
            kql = (
                f"ContainerInstanceLog_CL | where ContainerGroup_s == '{deployment_name}' "
                "| project TimeGenerated, Message | sort by TimeGenerated desc | limit 100 | sort by TimeGenerated asc"
            )
            self._run_cmd([
                "az",
                "monitor",
                "log-analytics",
                "query",
                "-w",
                ws_id,
                "--analytics-query",
                kql,
                "-o",
                "table",
            ])
        except Exception as exc:  # pragma: no cover
            click.echo(f"Failed to query Log Analytics: {exc}")

    @_catch_exceptions
    def put_secret(self, name: str, value: str) -> str:  # noqa: D401
        subscription_id, region, resource_group = self._check_prereqs()
        vault_name = os.getenv("AZURE_KEY_VAULT", "agentstr-kv")
        # Ensure vault exists
        show_cmd = [
            "az",
            "keyvault",
            "show",
            "--name",
            vault_name,
            "--resource-group",
            resource_group,
            "--query",
            "name",
            "-o",
            "tsv",
        ]
        result = subprocess.run(show_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            click.echo(f"Creating Key Vault '{vault_name}' ...")
            self._run_cmd([
                "az",
                "keyvault",
                "create",
                "--name",
                vault_name,
                "--resource-group",
                resource_group,
                "--location",
                region,
            ])
        name = name.replace("_", "-")
        # Set secret
        set_cmd = [
            "az",
            "keyvault",
            "secret",
            "set",
            "--vault-name",
            vault_name,
            "--name",
            name,
            "--value",
            value,
            "-o",
            "json",
        ]
        out = subprocess.check_output(set_cmd, text=True)
        uri = json.loads(out)["id"]
        click.echo(f"Secret '{name}' stored in Key Vault '{vault_name}'.")
        return uri

    @_catch_exceptions
    def provision_database(self, deployment_name: str) -> tuple[str, str]:  # noqa: D401
        """Provision Azure Database for PostgreSQL Flexible Server and store secret."""
        deployment_name = deployment_name.replace("_", "-")
        subscription_id, region, resource_group = self._check_prereqs()
        server_name = os.getenv("DATABASE_SERVER_NAME", "agentstr")
        admin_user = "agentuser"
        password = secrets.token_urlsafe(24)

        # ------------------------------------------------------------------
        # If Key Vault secret already exists, assume DB is provisioned. Reuse.
        # ------------------------------------------------------------------
        vault_name = os.getenv("AZURE_KEY_VAULT", "agentstr-kv")
        secret_name = f"agentstr-DATABASE_URL"
        pre_chk = subprocess.run([
            "az",
            "keyvault",
            "secret",
            "show",
            "--vault-name",
            vault_name,
            "--name",
            secret_name,
            "--query",
            "id",
            "-o",
            "tsv",
        ], capture_output=True, text=True)
        if pre_chk.returncode == 0:
            click.echo("Azure DB & DATABASE_URL secret already exist – reusing.")
            return "DATABASE_URL", pre_chk.stdout.strip()

        # Check existence
        show_cmd = [
            "az",
            "postgres",
            "flexible-server",
            "show",
            "--name",
            server_name,
            "--resource-group",
            resource_group,
            "--subscription",
            subscription_id,
            "-o",
            "json",
        ]
        exists = subprocess.run(show_cmd, capture_output=True)
    
        # If server exists already, attempt to reuse secret
        if exists.returncode == 0:
            show_secret = subprocess.run([
                "az",
                "keyvault",
                "secret",
                "show",
                "--vault-name",
                vault_name,
                "--name",
                secret_name,
                "--query",
                "id",
                "-o",
                "tsv",
            ], capture_output=True, text=True)
            if show_secret.returncode == 0:
                click.echo("Reusing existing DATABASE_URL secret.")
                return "DATABASE_URL", show_secret.stdout.strip()
            click.echo("Secret missing; resetting admin password and creating secret ...")
            # Reset password
            self._run_cmd([
                "az",
                "postgres",
                "flexible-server",
                "update",
                "--name",
                server_name,
                "--resource-group",
                resource_group,
                "--admin-password",
                password,
            ])
        else:
            click.echo("Creating Azure Postgres Flexible Server – may take a few minutes ...")
            self._run_cmd([
                "az",
                "postgres",
                "flexible-server",
                "create",
                "--name",
                server_name,
                "--resource-group",
                resource_group,
                "--location",
                region,
                "--admin-user",
                admin_user,
                "--admin-password",
                password,
                "--sku-name",
                "Standard_B1ms",
                "--tier",
                "Burstable",
                "--version",
                "15",
                "--public-access",
                "0.0.0.0-255.255.255.255",
                "--storage-size",
                "32",
                "--yes",
            ])
        # Build connection string
        host = f"{server_name}.postgres.database.azure.com"
        conn = f"postgresql://{admin_user}:{password}@{host}:5432/postgres?sslmode=require"
        secret_ref = self.put_secret(secret_name, conn)
        click.echo("Azure Postgres ready and secret stored.")
        return "DATABASE_URL", secret_ref

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
