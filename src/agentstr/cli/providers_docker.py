"""Docker provider for agentstr CLI using docker-compose."""
from __future__ import annotations

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, List
from agentstr.utils import default_metadata_file

import click

from .providers import Provider, register_provider, _catch_exceptions


@register_provider("docker")
class DockerProvider(Provider):
    """Docker provider using docker-compose for local deployments."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__("docker")
        self.compose_file = "docker-compose.yml"
        self._check_docker_prerequisites()

    def _check_docker_prerequisites(self):
        """Check if Docker and Docker Compose are installed."""
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise click.ClickException("Docker is not installed. Please install Docker before using this provider.")
        
        try:
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise click.ClickException("Docker Compose is not installed. Please install Docker Compose before using this provider.")

    def _run_cmd(self, cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run a shell command and return the result."""
        try:
            return subprocess.run(cmd, shell=False, check=True, cwd=cwd, capture_output=True, text=True)
        except subprocess.CalledProcessError as err:
            raise click.ClickException(f"Command failed: {err.stderr}") from err

    @_catch_exceptions
    def deploy(self, file_path: Path, deployment_name: str, *, secrets: Dict[str, str], **kwargs):  # noqa: D401
        deployment_name = f"agentstr-{deployment_name}"
        env = kwargs.get("env", {})
        dependencies = kwargs.get("dependencies", [])
        cpu = kwargs.get("cpu", 256)  # Not directly used in Docker Compose, for compatibility
        memory = kwargs.get("memory", 512)  # Not directly used in Docker Compose, for compatibility
        click.echo(
            f"[Docker] Deploying {file_path} as '{deployment_name}' (deps={dependencies}) ..."
        )
        
        # Remove existing container if it exists to avoid conflicts
        click.echo(f"[Docker] Removing any existing container named '{deployment_name}' ...")
        try:
            self._run_cmd(["docker", "rm", "-f", deployment_name])
            click.echo(f"[Docker] Existing container '{deployment_name}' removed.")
        except subprocess.CalledProcessError:
            click.echo(f"[Docker] No existing container named '{deployment_name}' found.")
        
        # Log secrets for debugging (masking sensitive values)
        click.echo("[Docker] Secrets being passed to container:")
        for key, value in secrets.items():
            status = "[empty or None]" if not value else "[value masked]"
            click.echo(f"[Docker] - {key}: {status}")
        
        # Create a temporary directory for the build context
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the file to the temp directory
            temp_file_path = Path(temp_dir) / file_path.name
            temp_file_path.write_text(file_path.read_text())
            deps_line = " " + " ".join(dependencies) if dependencies else ""
            if "agentstr-sdk" not in deps_line:
                deps_line = "agentstr-sdk[all] " + deps_line
            metadata_file = default_metadata_file(file_path)
            copy_metadata = ""
            if metadata_file:
                tmp_metadata_file = Path(temp_dir) / "nostr-metadata.yml"
                tmp_metadata_file.write_text(Path(metadata_file).read_text())
                copy_metadata = f"COPY nostr-metadata.yml /app/nostr-metadata.yml"

            # Create a Dockerfile
            dockerfile_content = f"""
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir {deps_line}
{copy_metadata}
COPY {file_path.name} /app/
CMD ["python", "/app/{file_path.name}"]
"""
            (Path(temp_dir) / "Dockerfile").write_text(dockerfile_content)
            
            # Create docker-compose.yml with a shared network
            network_name = "agentstr-network"
            compose_content = {
                "version": "3.8",
                "services": {
                    deployment_name: {
                        "build": ".",
                        "image": f"agentstr/{deployment_name}:latest",
                        "container_name": deployment_name,
                        "restart": "always",
                        "environment": [
                            f"{k}={v}" for k, v in env.items()
                        ] + [
                            f"{k}={v}" for k, v in secrets.items() if v is not None
                        ],
                        "networks": [network_name]
                    }
                },
                "networks": {
                    network_name: {
                        "driver": "bridge"
                    }
                }
            }

            import yaml
            (Path(temp_dir) / self.compose_file).write_text(yaml.dump(compose_content, default_flow_style=False))
            # Build and start the service
            self._run_cmd(["docker-compose", "up", "-d", "--build"], cwd=temp_dir)
            click.echo("Waiting for deployment to complete...")
            
            import time
            start_time = time.time()
            timeout_seconds = 600  # 10 minutes timeout
            poll_interval = 15  # Check every 15 seconds
            
            while time.time() - start_time < timeout_seconds:
                status_cmd = self._run_cmd(["docker", "ps", "--filter", f"name={deployment_name}", "--format", "{{.Status}}"], cwd=temp_dir)
                status = status_cmd.stdout.strip()
                if "Up" in status:
                    click.echo("Deployment completed.")
                    return
                elif "Exited" in status:
                    click.echo("Deployment failed: Container exited unexpectedly.")
                    import logging
                    logging.error(f"Deployment failed for {deployment_name}: Container exited unexpectedly")
                    return
                time.sleep(poll_interval)
            
            click.echo("Deployment timed out after 10 minutes.")
            import logging
            logging.error(f"Deployment timeout for {deployment_name} after 10 minutes")

    @_catch_exceptions
    def list(self, *, name_filter: Optional[str] = None):  # noqa: D401
        """List deployed services related to Agentstr."""
        cmd = ["docker", "ps", "--format", "{{.Names}} {{.Status}}"]
        if name_filter:
            cmd.extend(["--filter", f"name={name_filter}"])
        else:
            # Filter for containers related to Agentstr deployments (including database containers)
            cmd.extend(["--filter", "name=agentstr-*"])
        result = self._run_cmd(cmd)
        for line in result.stdout.splitlines():
            name, status = line.split(" ", 1)
            click.echo(f"{name} – status: {status}")

    @_catch_exceptions
    def logs(self, deployment_name: str, *, follow: bool = False):  # noqa: D401
        """Show logs for a deployment."""
        deployment_name = f"agentstr-{deployment_name}"
        cmd = ["docker", "logs", deployment_name]
        if follow:
            cmd.append("--follow")
        subprocess.run(cmd, shell=False, check=False)

    @_catch_exceptions
    def destroy(self, deployment_name: str):  # noqa: D401
        """Delete a deployment."""
        deployment_name = f"agentstr-{deployment_name}"
        click.echo(f"[Docker] Deleting deployment '{deployment_name}' ...")
        self._run_cmd(["docker", "rm", "-f", deployment_name])
        click.echo(f"Deployment '{deployment_name}' deleted.")

    @_catch_exceptions
    def put_secret(self, name: str, value: str) -> str:
        """Store a secret locally and return a reference. For Docker, we'll just return the name as reference."""
        click.echo(f"[Docker] Storing secret '{name}' locally.")
        # For local Docker deployments, we don't need to store secrets in a secret manager.
        # They will be passed directly as environment variables.
        return value

    @_catch_exceptions
    def provision_database(self, deployment_name: str) -> tuple[str, str]:
        deployment_name = f"agentstr-{deployment_name}"
        click.echo(f"[Docker] Provisioning local database for '{deployment_name}' ...")
        container_name = "agentstr-db"
        network_name = "agentstr-network"
        import subprocess
        try:
            # Check if container already exists
            result = self._run_cmd(["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"])
            if container_name in result.stdout:
                click.echo(f"Database container '{container_name}' already exists – reusing.")
            else:
                # Make sure network exists
                self._run_cmd(["docker", "network", "create", network_name], check=False)

                # Create a new database container
                self._run_cmd([
                    "docker", "run", "-d",
                    "--name", container_name,
                    "--restart", "always",
                    "-e", "POSTGRES_USER=postgres",
                    "-e", "POSTGRES_PASSWORD=postgres",
                    "-e", "POSTGRES_DB=agentstr",
                    "-v", f"{container_name}-data:/var/lib/postgresql/data",
                    "-p", "5432:5432",
                    "--network", network_name,
                    "postgres:15"
                ])
            return (
                "DATABASE_URL", f"postgresql://postgres:postgres@{container_name}:5432/agentstr"
            )
        except subprocess.CalledProcessError as e:
            import logging
            logging.error(f"Error provisioning database: {e}")
            raise
