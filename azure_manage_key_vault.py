import argparse
import sys
from typing import Iterable, List, Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import HttpResponseError


def list_secret_names(client: SecretClient, name_prefix: Optional[str]) -> List[str]:
    names: List[str] = []
    props_iter: Iterable = client.list_properties_of_secrets()
    for props in props_iter:
        name = props.name
        if name_prefix and not name.startswith(name_prefix):
            continue
        names.append(name)
    return names


def delete_secrets(client: SecretClient, names: List[str], purge: bool) -> None:
    for name in names:
        try:
            print(f"Deleting secret: {name}")
            poller = client.begin_delete_secret(name)
            poller.wait()
            print(f"Deleted (soft-delete) secret: {name}")
            if purge:
                try:
                    client.purge_deleted_secret(name)
                    print(f"Purged secret: {name}")
                except HttpResponseError as e:
                    # Purge may fail if soft-delete not enabled or insufficient permissions
                    print(f"Could not purge {name}: {e}")
        except HttpResponseError as e:
            print(f"Error deleting {name}: {e}")


def manage_key_vault(vault_url: str, name_prefix: Optional[str], force: bool, dry_run: bool, purge: bool) -> None:
    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)
        scope_desc = f"with name prefix '{name_prefix}'" if name_prefix else "(all secrets)"
        print(f"Fetching secrets from Key Vault: {vault_url} {scope_desc} ...")

        names = list_secret_names(client, name_prefix=name_prefix)
        if not names:
            print("No secrets found.")
            return

        print(f"\nFound {len(names)} secrets:")
        for n in names:
            print(f"  - {n}")

        if dry_run:
            print("\nDry run: no deletions will be performed.")
            return

        if not force:
            ans = input("\nProceed to delete ALL listed secrets? Type 'yes' to confirm: ").strip().lower()
            if ans != 'yes':
                print("Aborting. No secrets deleted.")
                return

        print("\nDeleting secrets...")
        delete_secrets(client, names, purge=purge)
        print("\nKey Vault cleanup finished.")

    except KeyboardInterrupt:
        print("Interrupted.")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List and delete Azure Key Vault secrets.")
    parser.add_argument("--vault-url", required=True, help="Key Vault URL, e.g., https://myvault.vault.azure.net/")
    parser.add_argument("--name-prefix", help="Optional name prefix filter for secrets.")
    parser.add_argument("--force", action="store_true", help="Do not prompt for confirmation; delete immediately.")
    parser.add_argument("--dry-run", action="store_true", help="Only list secrets; do not delete.")
    parser.add_argument("--purge", action="store_true", help="After deletion, purge secrets (if soft-delete enabled).")
    args = parser.parse_args()

    manage_key_vault(
        vault_url=args.vault_url,
        name_prefix=args.name_prefix,
        force=args.force,
        dry_run=args.dry_run,
        purge=args.purge,
    )
