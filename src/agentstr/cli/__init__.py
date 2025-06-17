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
from typing import Optional

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
    "--provider",
    type=click.Choice(PROVIDER_CHOICES, case_sensitive=False),
    callback=_resolve_provider,
    help="Cloud provider to target (default taken from $AGENTSTR_PROVIDER).",
    expose_value=True,
    is_eager=True,
)
@click.pass_context
def cli(ctx: click.Context, provider: str):  # noqa: D401
    """agentstr – lightweight IaC helper for Nostr MCP infrastructure."""
    ctx.obj = {"provider_name": provider.lower(), "provider": get_provider(provider.lower())}


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
    secrets_dict: dict[str, str] = {}
    env_dict: dict[str, str] = {}

    def _parse_kv(entries: tuple[str, ...], label: str, target: dict[str, str]):
        for ent in entries:
            if "=" not in ent:
                click.echo(f"Invalid {label} '{ent}'. Must be KEY=VALUE.", err=True)
                sys.exit(1)
            k, v = ent.split("=", 1)
            target[k] = v

    _parse_kv(secret, "--secret", secrets_dict)
    _parse_kv(env, "--env", env_dict)

    deps = list(dependency) if dependency else []

    if cpu is None:
        if provider.name == "aws":
            cpu = 256
        elif provider.name == "gcp":
            cpu = 0.25
        elif provider.name == "azure":
            cpu = 0.25
    elif provider.name == "gcp" or provider.name == "azure":
        cpu = cpu / 1000


    deployment_name = name or file_path.stem
    provider.deploy(
        file_path,
        deployment_name,
        secrets=secrets_dict,
        env=env_dict,
        dependencies=deps,
        cpu=cpu,
        memory=memory,
    )


@cli.command()
@click.option("--name", help="Filter by deployment name", required=False)
@click.pass_context
def list(ctx: click.Context, name: Optional[str]):  # noqa: D401
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
