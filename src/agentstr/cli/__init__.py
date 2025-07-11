"""Agentstr CLI for Infrastructure-as-Code operations.

The Agentstr CLI provides a command-line interface for deploying and managing agent applications on various cloud providers.

Usage:
    agentstr deploy <path_to_file> [--provider aws|gcp|azure|docker] [--name NAME]
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
import importlib.metadata
from typing_extensions import Annotated

import yaml

import click

from .providers import get_provider, Provider


def _get_provider(ctx: click.Context, cfg: Dict[str, Any] | None = None) -> Provider:
    """Return Provider instance from ctx or config, else error.

    Args:
        ctx: Click context object containing command state.
        cfg: Optional configuration dictionary to extract provider information from.

    Returns:
        Provider: An instance of the cloud provider class.

    Raises:
        click.ClickException: If provider is not specified via flag, environment variable, or config.
    """
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
PROVIDER_CHOICES = ["aws", "gcp", "azure", "docker"]


def _resolve_provider(ctx: click.Context, param: click.Parameter, value: Optional[str]):
    """Resolve provider from flag or env; may return None to allow config fallback.

    Args:
        ctx: Click context object containing command state.
        param: Click parameter object for the provider option.
        value: Optional value provided via command line flag.

    Returns:
        Optional[str]: Provider name if resolved from flag or environment, None otherwise.
    """
    if value:
        return value
    env_val = os.getenv(DEFAULT_PROVIDER_ENV)
    if env_val:
        return env_val
    # Defer error until after config is loaded
    return None


def _resolve_config_path(config_path: Path | None) -> Path | None:
    """Return config path from flag or $AGENTSTR_CONFIG env var (if flag is None).

    Args:
        config_path: Optional path to configuration file provided via flag.

    Returns:
        Path | None: Resolved path to configuration file or None if not specified.
    """
    if config_path is not None:
        return config_path
    ctx_val = click.get_current_context(silent=True)
    if ctx_val is not None and "config_path" in ctx_val.obj:
        return Path(ctx_val.obj["config_path"])
    env_val = os.getenv(DEFAULT_CONFIG_ENV)
    if env_val:
        return Path(env_val)
    return None


def _store_config_path(ctx: click.Context, _param: click.Parameter, value: Path | None):
    """Early callback to save --config path so subcommands can access regardless of position.

    Args:
        ctx: Click context object to store the config path.
        _param: Click parameter object (unused).
        value: Path to config file if provided, None otherwise.

    Returns:
        Path | None: The provided config path value (unchanged).
    """
    if not value:
        return None
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj.setdefault("config_path", value)
    return None


def _load_config(ctx: click.Context, config_path: Path | None) -> Dict[str, Any]:
    """Load config from YAML file (flag or env var).

    Args:
        ctx: Click context object containing command state.
        config_path: Optional path to configuration file.

    Returns:
        Dict[str, Any]: Configuration data loaded from YAML file, empty dict if no file.

    Raises:
        click.ClickException: If YAML parsing fails.
    """
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
def cli(ctx: click.Context, provider: Optional[str]):
    """Agentstr CLI - Lightweight command-line interface for deploying Agentstr apps to cloud providers.

    This CLI tool simplifies the process of deploying and managing Agentstr applications across multiple cloud providers.
    Use the subcommands to initialize projects, deploy applications, manage deployments, and more.

    Args:
        ctx: Click context object to store state across commands.
        provider: Optional provider name specified via flag or environment variable.
    """
    ctx.ensure_object(dict)
    if provider is not None:
        ctx.obj["provider_name"] = provider.lower()
        ctx.obj["provider"] = get_provider(provider.lower())


@cli.command()
@click.argument("file-path", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=False)
@click.option(
    "-f",
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML config file.",
)
@click.option(
    "-n",
    "--name",
    type=str,
    help="Unique name for this deployment (default derived from file-path or config).",
)
@click.option(
    "-s",
    "--secret",
    type=str,
    multiple=True,
    help="Secrets as KEY=VALUE pairs (can be repeated).",
)
@click.option(
    "-e",
    "--env",
    type=str,
    multiple=True,
    help="Environment variables as KEY=VALUE pairs (can be repeated).",
)
@click.option(
    "-d",
    "--dependency",
    type=str,
    multiple=True,
    help="Extra pip dependencies (can be repeated).",
)
@click.option(
    "--env-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to .env file with KEY=VALUE lines.",
)
@click.option(
    "--cpu",
    type=int,
    help="""Requested CPU cores (default 256 for AWS, 0.25 for GCP/Azure).""",
)
@click.option(
    "--memory",
    type=int,
    help="""Requested memory in MB (default 512).""",
    default=512,
)
@click.option(
    "--database/--no-database",
    is_flag=True,
    default=None,
    help="Whether to provision a postgres database (default derived from config).",
)
@click.pass_context
def deploy(
    ctx: click.Context,
    file_path: Path | None,
    config: Path | None,
    name: str | None,
    secret: tuple[str, ...],
    env: tuple[str, ...],
    dependency: tuple[str, ...],
    env_file: Path | None,
    cpu: int | None,
    memory: int,
    database: bool | None,
):
    """Deploy an application file (server or agent) to the chosen provider.

    If ``file-path`` is omitted, it will be resolved from the config file's ``file_path`` field.
    If no config file is provided, a ``file-path`` argument is required.

    Args:
        ctx: Click context object containing command state.
        file_path: Path to the application file to deploy.
        config: Path to YAML configuration file.
        name: Unique name for the deployment.
        secret: Tuple of secret key-value pair strings.
        env: Tuple of environment variable key-value pair strings.
        dependency: Tuple of additional pip dependencies.
        env_file: Path to .env file with environment variables.
        cpu: Requested CPU cores.
        memory: Requested memory in MB.
        database: Flag to provision a PostgreSQL database.

    Raises:
        click.ClickException: If required parameters are missing or invalid.
    """
    cfg = _load_config(ctx, config)
    provider = _get_provider(ctx, cfg)

    # Resolve file_path: CLI > config
    if file_path is None:
        file_path = cfg.get("file_path")
        if not file_path:
            raise click.ClickException("You must provide a file-path argument or set 'file_path' in the config file.")
        file_path = Path(file_path)
        if not file_path.exists():
            raise click.ClickException(f"Configured file_path '{file_path}' does not exist.")

    # Resolve deployment_name: CLI > config > file_path stem
    deployment_name = name or cfg.get("name") or file_path.stem

    def _parse_kv(entries: tuple[str, ...], label: str, target: dict[str, str]):
        """Parse key-value pairs from command line arguments.

        Args:
            ctx: Click context object (unused in this function).
            entries: Tuple of strings in KEY=VALUE format.
            label: Label for error messages.
            target: Dictionary to store parsed key-value pairs.

        Raises:
            click.ClickException: If a key-value pair is malformed.
        """
        for ent in entries:
            if "=" not in ent:
                click.echo(f"Invalid {label} '{ent}'. Must be KEY=VALUE.", err=True)
                sys.exit(1)
            k, v = ent.split("=", 1)
            target[k] = v

    # Resolve secrets, with a clear precedence: CLI > config > env_file
    secrets_dict: dict[str, str] = {}

    # 1. Load from env_file (from config or CLI)
    env_file_path = env_file or cfg.get("env_file")
    if env_file_path:
        env_file_path = Path(env_file_path)
        if not env_file_path.exists():
            raise click.ClickException(f"env_file path '{env_file_path}' does not exist.")
        click.echo(f"Loading secrets from {env_file_path}...")
        for raw_line in env_file_path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                click.echo(f"Skipping invalid line in {env_file_path}: {raw_line}", err=True)
                continue
            key, val = line.split("=", 1)
            # remove non-alphanumeric characters from deployment_name
            deployment_name_safe = "".join(c for c in deployment_name if c.isalnum())
            secret_ref = provider.put_secret(f'AGENTSTR-{deployment_name_safe}-{key.strip()}', val.strip())
            secrets_dict[key.strip()] = secret_ref

    # 2. Load from config 'secrets', overwriting env_file
    config_secrets = cfg.get("secrets", {})
    if config_secrets:
        secrets_dict.update(config_secrets)

    # 3. Load from CLI '--secret', overwriting all others
    _parse_kv(secret, "secret", secrets_dict)

    # Resolve environment variables: CLI > config
    env_dict: dict[str, str] = dict(cfg.get("env", {}))
    _parse_kv(env, "env", env_dict)

    # Remove secrets if present in env_dict
    for key in env_dict:
        if key in secrets_dict:
            del secrets_dict[key]

    # Resolve dependencies: CLI + config
    deps = list(cfg.get("extra_pip_deps", []))
    deps.extend(dependency)

    # Resolve CPU and Memory: CLI > config > provider default
    if cpu is None:
        cpu = cfg.get("cpu")
    if cpu is None:
        if provider.name == "aws":
            cpu = 256  # AWS uses integer units
        else:
            cpu = 0.25  # GCP/Azure use fractional vCPU
    if provider.name in {"gcp", "azure"} and isinstance(cpu, int) and cpu > 4:
        cpu = cpu / 1000

    if memory == 512:  # default flag value, so check config
        memory = cfg.get("memory", 512)

    # Handle database provisioning
    cfg_db = cfg.get("database")
    if database is None:
        database = bool(cfg_db)
    if database:
        click.echo("Provisioning managed Postgres database ...")
        env_key, secret_ref = provider.provision_database(deployment_name)
        secrets_dict[env_key] = secret_ref

    # Deploy
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
@click.option(
    "-f",
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML config file.",
)
@click.option(
    "-n",
    "--name",
    type=str,
    help="Filter by deployment name.",
)
@click.pass_context
def list_cmd(ctx: click.Context, config: Path | None, name: Optional[str]):
    """List active deployments on the chosen provider.

    Args:
        ctx: Click context object containing command state.
        config: Path to YAML configuration file.
        name: Optional name to filter deployments.
    """
    cfg = _load_config(ctx, config)
    provider = _get_provider(ctx, cfg)
    provider.list(name_filter=name)


@cli.command()
@click.argument("name", required=False)
@click.option(
    "-f",
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML config file.",
)
@click.pass_context
def logs(ctx: click.Context, name: str | None, config: Path | None):
    """Fetch logs for a deployment.

    If ``name`` is omitted, it will be resolved from the config file's ``name`` field
    or derived from the ``file_path`` stem.

    Args:
        ctx: Click context object containing command state.
        name: Name of the deployment to fetch logs for.
        config: Path to YAML configuration file.

    Raises:
        click.ClickException: If name cannot be resolved.
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
@click.argument("project-name")
@click.option("--force", is_flag=True, help="Overwrite directory if it exists")
@click.pass_context
def init_cmd(ctx: click.Context, project_name: str, force: bool):
    """Initialize a new Agentstr agent project skeleton in ``project-name`` directory.

    The generated template includes a minimal ``main.py`` that starts an in-memory
    agent with echo behavior plus a ``requirements.txt`` file. This aims to make
    the :doc:`../getting_started` guide work out-of-the-box::

        agentstr init my_agent
        python my_agent/main.py

    Args:
        ctx: Click context object (unused in this function).
        project_name: Name of the directory to create the project in.
        force: Overwrite existing directory if it exists.

    Raises:
        click.ClickException: If directory exists and --force is not specified.
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

    name = project_dir.name

    try:
        version = importlib.metadata.version("agentstr-sdk")
        sdk_dep = f"agentstr-sdk[cli]=={version}"
    except importlib.metadata.PackageNotFoundError:
        sdk_dep = "agentstr-sdk[cli]"

    # Write template files --------------------------------------------------
    (project_dir / "__init__.py").touch(exist_ok=True)

    main_py = dedent(
        '''\
"""Minimal Agentstr agent - says hello to users."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from agentstr import AgentstrAgent, ChatInput, metadata_from_yaml


# Define an agent callable
async def hello_world_agent(chat: ChatInput) -> str:
    return f"Hello {chat.user_id}!"


# Define the Agent
async def main():
    agent = AgentstrAgent(
        name="HelloWorldAgent",
        description="A minimal example that greets users.",
        nostr_metadata=metadata_from_yaml(__file__),
        agent_callable=hello_world_agent,
    )
    await agent.start()


# Run the server
if __name__ == "__main__":
    asyncio.run(main())
'''
    )
    (project_dir / "main.py").write_text(main_py)

    (project_dir / "requirements.txt").write_text(f"{sdk_dep}\n")

    from pynostr.key import PrivateKey
    key = PrivateKey()
    nsec = key.bech32()
    pubkey = key.public_key.bech32()
    (project_dir / ".env").write_text(f"""NOSTR_RELAYS=ws://localhost:6969
NOSTR_NSEC={nsec}
NOSTR_PUBKEY={pubkey}
NWC_CONN_STR=
LLM_MODEL_NAME=
LLM_BASE_URL=
LLM_API_KEY=
""")

    gitignore = """# Python-generated files
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
*.sqlite3
*.sqlite3*
*.db-*
"""

    (project_dir / ".gitignore").write_text(gitignore)
    (project_dir / ".dockerignore").write_text(gitignore)

    (project_dir / "README.md").write_text("""# Agentstr Agent Skeleton

This is a minimal example of an Agentstr agent that greets users.

#### To run it, first install the dependencies:

`pip install -r requirements.txt`

#### Then start the local relay:

`agentstr relay start`

#### Then run it:

`python main.py`

#### You can now test the agent with the test_client.py script:

`python test_client.py`
""")

    test_client_py = """from dotenv import load_dotenv
load_dotenv()

import os
from agentstr import NostrClient, PrivateKey

agent_pubkey = os.getenv("NOSTR_PUBKEY")

async def chat():
    client = NostrClient(private_key=PrivateKey().bech32())
    response = await client.send_direct_message_and_receive_response(
        agent_pubkey,
        "Hello",
    )
    print(response.message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat())
"""

    (project_dir / "test_client.py").write_text(test_client_py)

    # Default nostr-metadata.yml
    metadata = {
        "name": name,
        "display_name": name,
        "username": name,
        "about": "A minimal example of an Agentstr agent that greets users.",
        "picture": "https://agentstr.com/favicon.ico",
        "banner": "",
        "website": "https://agentstr.com",
    }
    (project_dir / "nostr-metadata.yml").write_text(yaml.safe_dump(metadata))
    
    # Create cloud deployment configs
    main_path = os.path.join(project_name, "main.py")
    env_path = os.path.join(project_name, ".env")
    #requirements_path = os.path.join(project_name, "requirements.txt")

    deploy_config = f"""name: {name}  # Deployment name

file_path: {main_path}  # Path to main.py file

database: true  # Provision postgres database (if not already provisioned)

extra_pip_deps:  # Additional Python deps installed in image
  - {sdk_dep}

env:  # Environment Variables
  NOSTR_RELAYS: wss://relay.primal.net,wss://relay.damus.io,wss://nostr.mom

env_file: {env_path}  # Path to .env file
"""

    (project_dir / "deploy.yml").write_text(deploy_config)

    click.echo(f"✅ Project skeleton created in {project_dir}")

# ---------------------------------------------------------------------------
# Local Relay helper (dev-only)
# ---------------------------------------------------------------------------

@cli.group()
@click.pass_context
def relay(ctx: click.Context):
    """Utilities for running lightweight local Nostr relays.

    Args:
        ctx: Click context object (unused in this function).
    """
    pass


@relay.command("start")
@click.option("--config", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def relay_start(ctx: click.Context, config: Path):
    """Spawn a local Nostr relay instance using a YAML config file.

    The command maps directly to::

        nostr-relay serve --config CONFIG_FILE

    See example config at:
    https://code.pobblelabs.org/nostr_relay/file?name=nostr_relay/config.yaml

    Args:
        ctx: Click context object (unused in this function).
        config: Path to YAML configuration file for the relay.

    Raises:
        click.ClickException: If 'nostr-relay' CLI is not installed.
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
def put_secret(ctx: click.Context, key: str, value: str | None, config: Path | None, value_file: Path | None):
    """Create or update a cloud-provider secret and return its reference string.

    VALUE may be provided directly or via --value-file.

    Args:
        ctx: Click context object containing command state.
        key: Secret key name.
        value: Secret value (optional if using --value-file).
        config: Path to YAML configuration file.
        value_file: Path to file containing secret value.

    Raises:
        click.ClickException: If neither VALUE nor --value-file is provided.
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


@cli.command()
@click.argument("name", required=False)
@click.option("-f", "--config", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Path to YAML config file.")
@click.pass_context
def destroy(ctx: click.Context, name: str | None, config: Path | None):
    """Destroy a deployment.

    Args:
        ctx: Click context object containing command state.
        name: Name of the deployment to destroy.
        config: Path to YAML configuration file.

    Raises:
        click.ClickException: If name cannot be resolved.
    """
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


def main() -> None:
    """Entry point for `python -m agentstr.cli`.

    Runs the Agentstr CLI tool.
    """
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
