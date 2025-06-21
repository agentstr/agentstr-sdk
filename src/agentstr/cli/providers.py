"""Provider abstraction and stub implementations for agentstr CLI."""
from __future__ import annotations

import abc
from pathlib import Path
from typing import Dict, Optional

import json
from functools import wraps

import click


def _catch_exceptions(fn):  # noqa: D401
    """Decorator to convert any unexpected exception into ClickException."""

    @wraps(fn)
    def _wrapper(*args, **kwargs):  # noqa: D401
        try:
            return fn(*args, **kwargs)
        except click.ClickException:
            raise
        except Exception as err:  # pragma: no cover
            raise click.ClickException(str(err)) from err

    return _wrapper

PROVIDER_REGISTRY: dict[str, "Provider"] = {}


def register_provider(name: str):  # noqa: D401
    """Class decorator to register provider implementation.

    If a provider with the same name is already registered, the first
    """

    def _decorator(cls):  # noqa: D401
        PROVIDER_REGISTRY[name] = cls  # type: ignore[arg-type]
        return cls

    return _decorator


class Provider(abc.ABC):  # noqa: D401
    """Abstract provider interface."""

    def __init__(self, name: str) -> None:  # noqa: D401
        self.name = name

    # Core operations -----------------------------------------------------
    @abc.abstractmethod
    @_catch_exceptions
    def deploy(self, file_path: Path, deployment_name: str, *, secrets: Dict[str, str], **kwargs):  # noqa: D401
        """Deploy a file to the cloud provider."""

    @abc.abstractmethod
    @_catch_exceptions
    def list(self, *, name_filter: Optional[str] = None):  # noqa: D401
        """List deployments/resources."""

    @abc.abstractmethod
    @_catch_exceptions
    def logs(self, deployment_name: str):  # noqa: D401
        """Fetch logs for a deployment."""

    @abc.abstractmethod
    @_catch_exceptions
    def destroy(self, deployment_name: str):  # noqa: D401
        """Destroy/tear down a deployment."""

    # Database ------------------------------------------------------------
    @abc.abstractmethod
    @_catch_exceptions
    def provision_database(self, deployment_name: str) -> tuple[str, str]:  # noqa: D401
        """Provision a Postgres database and return (env_var_name, secret_ref).

        Implementations should create the database securely and store the
        resulting connection string in the provider's secret manager. The
        secret *reference* (ARN/URI/etc.) is returned so the CLI can attach it
        as a container secret. The *env_var_name* is the environment key that
        will be populated from that secret (e.g. ``DATABASE_URL``).
        """

    # Secrets -------------------------------------------------------------
    @abc.abstractmethod
    @_catch_exceptions
    def put_secret(self, name: str, value: str) -> str:  # noqa: D401
        """Create/update a secret and return its reference (ARN/URI/path)."""

    # Helper utilities ----------------------------------------------------
    def _serialize_secrets(self, secrets: Dict[str, str]) -> str:  # noqa: D401
        """Serialize secrets for passing to container env vars."""
        return json.dumps(secrets)


# -------------------- Provider Implementations moved to separate modules -----------------
# Keep backward compatibility by importing modules so they register themselves.

from . import providers_aws  # noqa: F401  pylint: disable=unused-import
from . import providers_gcp  # noqa: F401  pylint: disable=unused-import
from . import providers_azure  # noqa: F401  pylint: disable=unused-import

# (Legacy code below removed)



def _catch_exceptions(fn):  # noqa: D401
    """Decorator to convert any unexpected exception into a ClickException."""

    @wraps(fn)
    def _wrapper(self, *args, **kwargs):  # noqa: D401
        try:
            return fn(self, *args, **kwargs)
        except click.ClickException:
            raise
        except Exception as err:  # pragma: no cover
            raise click.ClickException(str(err)) from err

    return _wrapper


# -------------------- Factory --------------------------------------------


def get_provider(name: str) -> Provider:  # noqa: D401
    """Return provider instance by name."""
    name = name.lower()
    try:
        provider_cls = PROVIDER_REGISTRY[name]
    except KeyError as exc:  # pragma: no cover
        raise click.ClickException(f"Unknown provider '{name}'.") from exc
    return provider_cls()  # type: ignore[call-arg]
