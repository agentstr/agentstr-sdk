"""Azure provider stub implementation extracted from providers.py."""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Dict, Optional

import click

from .providers import _catch_exceptions, register_provider, Provider  # type: ignore


@register_provider("azure")
class AzureProvider(Provider):  # noqa: D401
    """Azure Container Instances stub implementation."""

    def __init__(self) -> None:  # noqa: D401
        super().__init__("azure")
        self._lazy_import("azure.mgmt.containerinstance", "azure-mgmt-containerinstance")

    # Utilities -----------------------------------------------------------
    def _lazy_import(self, module_name: str, pip_name: str):  # noqa: D401
        try:
            importlib.import_module(module_name)
        except ImportError:  # pragma: no cover
            click.echo(
                f"Azure provider requires {pip_name}. Install with 'pip install {pip_name}' to enable.",
                err=True,
            )
            raise

    # Provider interface --------------------------------------------------
    @_catch_exceptions
    def deploy(self, file_path: Path, deployment_name: str, *, secrets: Dict[str, str], **kwargs):  # noqa: D401
        click.echo(f"[Azure] Deploying {file_path} as '{deployment_name}' (stub)")

    @_catch_exceptions
    def list(self, *, name_filter: Optional[str] = None):  # noqa: D401
        click.echo("[Azure] Listing deployments (stub)")

    @_catch_exceptions
    def logs(self, deployment_name: str):  # noqa: D401
        click.echo(f"[Azure] Fetching logs for {deployment_name} (stub)")

    @_catch_exceptions
    def destroy(self, deployment_name: str):  # noqa: D401
        click.echo(f"[Azure] Destroying {deployment_name} (stub)")
