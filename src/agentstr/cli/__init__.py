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


def _get_provider(ctx: click.Context, cfg: Dict[str, Any] | None = None) -> Provider:  # noqa: D401
    """Return Provider instance from ctx or config, else error."""
    prov: Provider | None = ctx.obj.get("provider")
    if prov is not None:
        return prov
    prov_name: str | None = None
    if cfg:
        prov_name = cfg.get("provider")
    if not prov_name:
        raise click.ClickException(
            "Provider not specified. Use --provider flag, $AGENTSTR_PROVIDER env, or set 'provider' in the config file."
        )
    prov = get_provider(str(prov_name).lower())
    ctx.obj["provider"] = prov
    return prov

DEFAULT_PROVIDER_ENV = "AGENTSTR_PROVIDER"
DEFAULT_CONFIG_ENV = "AGENTSTR_CONFIG"
PROVIDER_CHOICES = ["aws", "gcp", "azure"]


def _resolve_provider(ctx: click.Context, param: click.Parameter, value: Optional[str]):  # noqa: D401
    """Resolve provider from flag or env; may return None to allow config fallback."""
    if value:
        return value
    env_val = os.getenv(DEFAULT_PROVIDER_ENV)
    if env_val:
        return env_val
    # Defer error until after config is loaded
    return None


def _resolve_config_path(config_path: Path | None) -> Path | None:  # noqa: D401
    """Return config path from flag or $AGENTSTR_CONFIG env var (if flag is None)."""
    if config_path is not None:
        return config_path
    ctx_val = click.get_current_context(silent=True)
    if ctx_val is not None and "config_path" in ctx_val.obj:
        return Path(ctx_val.obj["config_path"])
    env_val = os.getenv(DEFAULT_CONFIG_ENV)
    if env_val:
        return Path(env_val)
    return None


def _store_config_path(ctx: click.Context, _param: click.Parameter, value: Path | None):  # noqa: D401
    """Early callback to save --config path so subcommands can access regardless of position."""
    if not value:
        return None
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj.setdefault("config_path", value)
    return None


def _load_config(ctx: click.Context, config_path: Path | None) -> Dict[str, Any]:
    """Load config from YAML file (flag or env var)."""
    cfg_path = _resolve_config_path(config_path)
    config_data: Dict[str, Any] = {}
    if cfg_path is not None:
        try:
            config_data = yaml.safe_load(cfg_path.read_text()) or {}
        except Exception as exc:  # pragma: no cover
            raise click.ClickException(f"Failed to parse config YAML: {exc}")
    return config_data


@click.group()
@click.option(
    "--provider",
    type=click.Choice(PROVIDER_CHOICES, case_sensitive=False),
    callback=_resolve_provider,
    help="Cloud provider to target (default taken from $AGENTSTR_PROVIDER).",
    expose_value=True,
    is_eager=True,
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML config file.",
    expose_value=False,
    is_eager=True,
    callback=_store_config_path,
)
@click.pass_context
def cli(ctx: click.Context, provider: Optional[str]):  # noqa: D401
    """agentstr-cli – lightweight cli for deploying agentstr apps to cloud providers."""
    ctx.ensure_object(dict)
    if provider is not None:
        ctx.obj["provider_name"] = provider.lower()
        ctx.obj["provider"] = get_provider(provider.lower())



@cli.command()
@click.argument("file_path", required=False, type=click.Path(exists=True, path_type=Path))
@click.option("-f", "--config", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to YAML config file.")
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
@click.option(
    "--database/--no-database",
    default=None,
    help="Provision a managed Postgres database and inject DATABASE_URL secret.",
)
@click.option("--cpu", type=int, default=None, show_default=True, help="Cloud provider vCPU units (e.g. 256=0.25 vCPU).")
@click.option("--memory", type=int, default=512, show_default=True, help="Cloud provider memory (MiB).")
@click.pass_context
def deploy(ctx: click.Context, file_path: Path, config: Path | None, name: Optional[str], secret: tuple[str, ...], env: tuple[str, ...], dependency: tuple[str, ...], cpu: int | None, memory: int, database: bool | None):  # noqa: D401
    """Deploy an application file (server or agent) to the chosen provider."""
    cfg = _load_config(ctx, config)
    provider = _get_provider(ctx, cfg)
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

    # file_path argument is optional; fallback to config
    if file_path is None:
        file_path = cfg.get("file_path")
        if not file_path:
            raise click.ClickException("You must provide a file_path argument or set 'file_path' in the config file.")
        file_path = Path(file_path)
        if not file_path.exists():
            raise click.ClickException(f"Configured file_path '{file_path}' does not exist.")

    deployment_name = name or cfg.get("name") or file_path.stem

    # Handle database provisioning ------------------------------------
    cfg_db = cfg.get("database")
    if database is None:
        database = bool(cfg_db)
    if database:
        click.echo("Provisioning managed Postgres database ...")
        env_key, secret_ref = provider.provision_database(deployment_name)
        secrets_dict[env_key] = secret_ref
        if provider.name == "aws":
            secrets_dict["DATABASE_URL"] = secret_ref[:-7]


    # Continue with normal deploy -------------------------------------
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
@click.option("-f", "--config", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to YAML config file.")
@click.option("--name", help="Filter by deployment name", required=False)
@click.pass_context
def list_cmd(ctx: click.Context, config: Path | None, name: Optional[str]):  # noqa: D401
    """List active deployments on the chosen provider."""
    cfg = _load_config(ctx, config)
    provider = _get_provider(ctx, cfg)
    provider.list(name_filter=name)


@cli.command()
@click.argument("name", required=False)
@click.option("-f", "--config", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to YAML config file.")
@click.pass_context
def logs(ctx: click.Context, name: str | None, config: Path | None):  # noqa: D401
    """Fetch logs for a deployment.

    If NAME is omitted, it will be resolved from the config file's 'name' field or
    derived from the 'file_path' stem.
    """
    cfg = _load_config(ctx, config)
    if not name:
        # Try to resolve from config
        name = cfg.get("name")
        if not name:
            file_path = cfg.get("file_path")
            if file_path:
                name = Path(file_path).stem
        if not name:
            raise click.ClickException("You must provide a deployment NAME, set 'name', or set 'file_path' in the config file.")
    provider = _get_provider(ctx, cfg)
    provider.logs(name)


@cli.command("put-secret")
@click.argument("key")
@click.argument("value", required=False)
@click.option("-f", "--config", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to YAML config file.")
@click.option("--value-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Read secret value from file (overrides VALUE argument).")
@click.pass_context
def put_secret(ctx: click.Context, key: str, value: str | None, config: Path | None, value_file: Path | None):  # noqa: D401
    """Create or update a cloud-provider secret and return its reference string.

    VALUE may be provided directly or via --value-file.
    """
    # just load to validate path/env
    _ = _load_config(ctx, config)
    if value_file is not None:
        value = Path(value_file).read_text()
    if value is None:
        click.echo("Either VALUE argument or --value-file must be supplied.", err=True)
        sys.exit(1)
    provider = _get_provider(ctx, cfg)
    ref = provider.put_secret(key, value)
    click.echo(ref)


@cli.command("put-secrets")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-f", "--config", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to YAML config file.")
@click.pass_context
def put_secrets(ctx: click.Context, env_file: Path, config: Path | None):  # noqa: D401
    """Create or update multiple secrets from a .env file.

    ENV_FILE should contain KEY=VALUE lines (comments with # allowed). Each
    secret is stored via the provider's secret manager and the resulting
    reference printed.
    """
    cfg = _load_config(ctx, config)
    provider = _get_provider(ctx, cfg)
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
@click.argument("name", required=False)
@click.option("-f", "--config", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to YAML config file.")
@click.pass_context
def destroy(ctx: click.Context, name: str | None, config: Path | None):  # noqa: D401
    """Destroy a deployment."""
    cfg = _load_config(ctx, config)
    if not name:
        name = cfg.get("name")
        if not name:
            file_path = cfg.get("file_path")
            if file_path:
                name = Path(file_path).stem
        if not name:
            raise click.ClickException("You must provide a deployment NAME, set 'name', or set 'file_path' in the config file.")
    provider = _get_provider(ctx, cfg)
    provider.destroy(name)


def main() -> None:  # noqa: D401
    """Entry point for `python -m agentstr.cli`."""
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
