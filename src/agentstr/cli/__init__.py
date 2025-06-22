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
import subprocess
import shutil
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


# ---------------------------------------------------------------------------
# Project scaffolding helpers
# ---------------------------------------------------------------------------

@cli.command("init")
@click.argument("project_name")
@click.option("--force", is_flag=True, help="Overwrite PROJECT_NAME directory if it exists.")
@click.pass_context
def init_cmd(ctx: click.Context, project_name: str, force: bool):  # noqa: D401
    """Initialise a *new* Agentstr agent project skeleton in *PROJECT_NAME* directory.

    The generated template includes a minimal `main.py` that starts an in-memory
    agent with echo behaviour plus a `requirements.txt` file.  This aims to make
    the :doc:`getting_started` guide work out-of-the-box::

        agentstr init my_agent
        cd my_agent
        python -m venv .venv && source .venv/bin/activate
        pip install -r requirements.txt
        python main.py
    """
    from textwrap import dedent

    project_dir = Path(project_name).resolve()
    if project_dir.exists() and not force:
        raise click.ClickException(
            f"Directory '{project_dir}' already exists. Use --force to overwrite.")

    if project_dir.exists() and force:
        for p in project_dir.iterdir():
            if p.is_file():
                p.unlink()
            else:
                import shutil
                shutil.rmtree(p)
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write template files --------------------------------------------------
    (project_dir / "__init__.py").touch(exist_ok=True)

    main_py = dedent(
        '''\
"""Minimal Agentstr agent – echoes incoming messages."""

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from agentstr import AgentCard, NostrAgentServer, ChatInput, ChatOutput


async def echo_agent(chat: ChatInput) -> str | ChatOutput:  # noqa: D401
    return chat.messages[-1]


async def main() -> None:
    card = AgentCard(
        name="EchoAgent",
        description="A minimal example that echoes messages back.",
        nostr_pubkey=os.getenv("AGENT_PUBKEY"),
    )
    server = NostrAgentServer(
        agent_info=card,
        agent_callable=echo_agent,
        relays=[os.getenv("RELAY_URL")], 
        private_key=os.getenv("AGENT_NSEC"),
    )
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
'''
    )
    (project_dir / "main.py").write_text(main_py)

    (project_dir / "requirements.txt").write_text("agentstr-sdk[cli]\n")

    from pynostr.key import PrivateKey
    key = PrivateKey()
    nsec = key.bech32()
    pubkey = key.public_key.bech32()
    (project_dir / ".env").write_text(f"RELAY_URL=ws://localhost:6969\nAGENT_NSEC={nsec}\nAGENT_PUBKEY={pubkey}")

    (project_dir / ".gitignore").write_text("""# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

.pytest_cache/
.ruff_cache/

# Virtual environments
.venv

# Environment variables
.env

# IDEs
.idea/

.DS_Store

# Databases
*.db
*.sqlite*""")

    (project_dir / "README.md").write_text("""# Agentstr Agent Skeleton

This is a minimal example of an Agentstr agent that echoes messages back to the sender.

#### To run it, first install the dependencies:

`pip install -r requirements.txt`

#### Then start the local relay:

`agentstr relay run`

#### Then run it:

`python main.py`

#### You can now test the agent with the test_client.py script:

`python test_client.py`
""")

    test_client_py = """
from dotenv import load_dotenv
load_dotenv()

import os
from agentstr import NostrClient, PrivateKey

# Get the environment variables
relays = [os.getenv("RELAY_URL")]
agent_pubkey = os.getenv("AGENT_PUBKEY")


async def chat():
    client = NostrClient(relays, PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        agent_pubkey,
        "Hello, how are you?",
    )
    print(response.message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat())
"""

    (project_dir / "test_client.py").write_text(test_client_py)

    click.echo(f"✅ Project skeleton created in {project_dir}")

# ---------------------------------------------------------------------------
# Local Relay helper (dev-only)
# ---------------------------------------------------------------------------

@cli.group()
@click.pass_context
def relay(ctx: click.Context):  # noqa: D401
    """Utilities for running lightweight local Nostr relays."""


@relay.command("run")
@click.option("--config", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def relay_run(ctx: click.Context, config: Path):  # noqa: D401
    """Spawn a local *nostr-relay* instance using a YAML CONFIG_FILE.

    The command maps directly to::

        nostr-relay serve --config CONFIG_FILE

    See example config at:
    https://code.pobblelabs.org/nostr_relay/file?name=nostr_relay/config.yaml
    """
    # Ensure nostr-relay CLI is available
    if shutil.which("nostr-relay") is None:  # pragma: no cover
        click.echo(
            "The 'nostr-relay' CLI is not installed or not on PATH. Install it via\n"
            "\n    pip install nostr-relay\n",
            err=True,
        )
        sys.exit(1)

    # Build command
    if config is None:
        cmd = ["nostr-relay", "serve"]
    else:
        cmd = ["nostr-relay", "serve", "--config", str(config)]

    click.echo(f"Executing: {' '.join(cmd)}")
    # Forward control; when relay exits, we return.
    subprocess.run(cmd, check=True)

# ---------------------------------------------------------------------------

@click.argument("key")
@click.argument("value", required=False)
@click.option("-f", "--config", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to YAML config file.")
@click.option("--value-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Read secret value from file (overrides VALUE argument).")
@click.pass_context
def put_secret(ctx: click.Context, key: str, value: str | None, config: Path | None, value_file: Path | None):  # noqa: D401
    """Create or update a cloud-provider secret and return its reference string.

    VALUE may be provided directly or via --value-file.
    """
    # Load config (needed for provider resolution)
    cfg = _load_config(ctx, config)
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
