"""agentstr CLI for Infrastructure-as-Code operations.

Usage:
    agentstr deploy <path_to_file> [--provider aws|gcp|azure] [--name NAME]
    agentstr list [--provider ...]
    agentstr logs <name> [--provider ...]
    agentstr destroy <name> [--provider ...]

The provider can also be set via the environment variable ``AGENTSTR_PROVIDER``.
Secrets can be provided with multiple ``--secret KEY=VALUE`` flags.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import yaml

import click

from .providers import get_provider, Provider

DEFAULT_PROVIDER_ENV = "AGENTSTR_PROVIDER"
PROVIDER_CHOICES = ["aws", "gcp", "azure"]


def _resolve_provider(ctx: click.Context, param: click.Parameter, value: Optional[str]):  # noqa: D401
    """Callback to resolve provider from flag or env var."""
    if value:
        return value
    env_val = os.getenv(DEFAULT_PROVIDER_ENV)
    if env_val:
        return env_val
    # Fallback default
    return "aws"


@click.group()
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML config file.",
    is_eager=True,
)
@click.option(
    "--provider",
    type=click.Choice(PROVIDER_CHOICES, case_sensitive=False),
    callback=_resolve_provider,
    help="Cloud provider to target (default taken from $AGENTSTR_PROVIDER).",
    expose_value=True,
    is_eager=True,
)
@click.pass_context
def cli(ctx: click.Context, config: Path | None, provider: str):  # noqa: D401
    """agentstr – lightweight IaC helper for Nostr MCP infrastructure."""
    config_data: Dict[str, Any] = {}
    if config is not None:
        try:
            config_data = yaml.safe_load(config.read_text()) or {}
        except Exception as exc:  # pragma: no cover
            raise click.ClickException(f"Failed to parse config YAML: {exc}")

    # If provider not explicitly set, take from config file
    if provider == _resolve_provider(None, None, None) and config_data.get("provider"):
        provider = str(config_data["provider"]).lower()

    ctx.obj = {
        "provider_name": provider.lower(),
        "provider": get_provider(provider.lower()),
        "config": config_data,
    }


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option("--name", help="Deployment name", required=False)
@click.option(
    "--secret",
    multiple=True,
    help="Secret in KEY=VALUE format. Can be supplied multiple times.",
)
@click.option(
    "--env",
    multiple=True,
    help="Environment variable KEY=VALUE to inject. Can be supplied multiple times.",
)
@click.option(
    "--pip",
    "dependency",
    multiple=True,
    help="Additional Python package (pip install) to include in the container. Repeatable.",
)
@click.option("--cpu", type=int, default=None, show_default=True, help="Cloud provider vCPU units (e.g. 256=0.25 vCPU).")
@click.option("--memory", type=int, default=512, show_default=True, help="Cloud provider memory (MiB).")
@click.pass_context
def deploy(ctx: click.Context, file_path: Path, name: Optional[str], secret: tuple[str, ...], env: tuple[str, ...], dependency: tuple[str, ...], cpu: int | None, memory: int):  # noqa: D401
    """Deploy an application file (server or agent) to the chosen provider."""
    provider: Provider = ctx.obj["provider"]
    cfg = ctx.obj.get("config", {})
    secrets_dict: dict[str, str] = dict(cfg.get("secrets", {}))
    env_dict: dict[str, str] = dict(cfg.get("env", {}))

    def _parse_kv(entries: tuple[str, ...], label: str, target: dict[str, str]):
        for ent in entries:
            if "=" not in ent:
                click.echo(f"Invalid {label} '{ent}'. Must be KEY=VALUE.", err=True)
                sys.exit(1)
            k, v = ent.split("=", 1)
            target[k] = v

    _parse_kv(secret, "--secret", secrets_dict)
    _parse_kv(env, "--env", env_dict)

    deps = list(cfg.get("extra_pip_deps", []))
    if dependency:
        deps.extend(dependency)

    if cpu is None:
        cpu = cfg.get("cpu")
    if cpu is None:
        if provider.name == "aws":
            cpu = 256
        else:
            cpu = 0.25
    # For gcp/azure convert millicore if user provided int >=100
    if provider.name in {"gcp", "azure"} and isinstance(cpu, int) and cpu > 4:
        cpu = cpu / 1000


    if memory == 512:  # default flag value, check config override
        memory = cfg.get("memory", memory)

    deployment_name = name or cfg.get("name") or file_path.stem
    provider.deploy(
        file_path,
        deployment_name,
        secrets=secrets_dict,
        env=env_dict,
        dependencies=deps,
        cpu=cpu,
        memory=memory,
    )


@cli.command(name="list")
@click.option("--name", help="Filter by deployment name", required=False)
@click.pass_context
def list_cmd(ctx: click.Context, name: Optional[str]):  # noqa: D401
    """List active deployments on the chosen provider."""
    provider: Provider = ctx.obj["provider"]
    provider.list(name_filter=name)


@cli.command()
@click.argument("name")
@click.pass_context
def logs(ctx: click.Context, name: str):  # noqa: D401
    """Fetch logs for a deployment."""
    provider: Provider = ctx.obj["provider"]
    provider.logs(name)


@cli.command("put-secret")
@click.argument("key")
@click.argument("value", required=False)
@click.option("--value-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Read secret value from file (overrides VALUE argument).")
@click.pass_context
def put_secret(ctx: click.Context, key: str, value: str | None, value_file: Path | None):  # noqa: D401
    """Create or update a cloud-provider secret and return its reference string.

    VALUE may be provided directly or via --value-file.
    """
    if value_file is not None:
        value = Path(value_file).read_text()
    if value is None:
        click.echo("Either VALUE argument or --value-file must be supplied.", err=True)
        sys.exit(1)
    provider: Provider = ctx.obj["provider"]
    ref = provider.put_secret(key, value)
    click.echo(ref)


@cli.command("put-secrets")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def put_secrets(ctx: click.Context, env_file: Path):  # noqa: D401
    """Create or update multiple secrets from a .env file.

    ENV_FILE should contain KEY=VALUE lines (comments with # allowed). Each
    secret is stored via the provider's secret manager and the resulting
    reference printed.
    """
    provider: Provider = ctx.obj["provider"]
    count = 0
    for raw_line in Path(env_file).read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            click.echo(f"Skipping invalid line: {raw_line}", err=True)
            continue
        key, val = line.split("=", 1)
        ref = provider.put_secret(key, val)
        click.echo(f"{key} -> {ref}")
        count += 1
    click.echo(f"Stored {count} secrets.")


@cli.command()
@click.argument("name")
@click.pass_context
def destroy(ctx: click.Context, name: str):  # noqa: D401
    """Destroy a deployment."""
    provider: Provider = ctx.obj["provider"]
    provider.destroy(name)


def main() -> None:  # noqa: D401
    """Entry point for `python -m agentstr.cli`."""
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
