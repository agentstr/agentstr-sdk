import argparse
import sys
from typing import List, Optional

import boto3
import botocore


def list_parameters(client, prefix: Optional[str], recursive: bool) -> List[str]:
    names: List[str] = []
    if prefix:
        paginator = client.get_paginator('get_parameters_by_path')
        for page in paginator.paginate(Path=prefix, Recursive=recursive, WithDecryption=False):
            for p in page.get('Parameters', []):
                names.append(p['Name'])
    else:
        paginator = client.get_paginator('describe_parameters')
        for page in paginator.paginate():
            for meta in page.get('Parameters', []):
                # describe_parameters returns metadata including Name
                names.append(meta['Name'])
    return names


essm_delete_batch_size = 10  # delete_parameters API supports up to 10 at a time

def delete_parameters(client, names: List[str]) -> None:
    for i in range(0, len(names), essm_delete_batch_size):
        batch = names[i:i + essm_delete_batch_size]
        resp = client.delete_parameters(Names=batch)
        deleted = resp.get('DeletedParameters', [])
        invalid = resp.get('InvalidParameters', [])
        if deleted:
            print(f"Deleted: {', '.join(deleted)}")
        if invalid:
            print(f"Invalid (not found or no access): {', '.join(invalid)}")


def manage_parameter_store(region: Optional[str], prefix: Optional[str], recursive: bool, force: bool, dry_run: bool) -> None:
    try:
        client = boto3.client('ssm', region_name=region)
        resolved_region = region or client.meta.region_name
        scope_desc = f"prefix '{prefix}' (recursive={recursive})" if prefix else "all parameters"
        print(f"Fetching {scope_desc} from AWS SSM Parameter Store in region: {resolved_region}...")

        param_names = list_parameters(client, prefix=prefix, recursive=recursive)
        if not param_names:
            print("No parameters found.")
            return

        print(f"\nFound {len(param_names)} parameters.")
        for n in param_names:
            print(f"  - {n}")

        if dry_run:
            print("\nDry run: no deletions will be performed.")
            return

        if not force:
            ans = input("\nProceed to delete ALL listed parameters? Type 'yes' to confirm: ").strip().lower()
            if ans != 'yes':
                print("Aborting. No parameters deleted.")
                return

        print("\nDeleting parameters...")
        delete_parameters(client, param_names)
        print("\nParameter Store cleanup finished.")

    except botocore.exceptions.NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
        sys.exit(1)
    except botocore.exceptions.ClientError as e:
        print(f"AWS client error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted.")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List and delete AWS SSM Parameter Store parameters.')
    parser.add_argument('--region', type=str, help='AWS region to use. Defaults to your environment configuration if omitted.')
    parser.add_argument('--prefix', type=str, help='Optional path prefix to filter parameters, e.g. /my/app. If omitted, operates on all parameters.')
    parser.add_argument('--recursive', action='store_true', help='When used with --prefix, include all child paths recursively.')
    parser.add_argument('--force', action='store_true', help='Do not prompt for confirmation; delete immediately.')
    parser.add_argument('--dry-run', action='store_true', help='Only list parameters; do not delete.')
    args = parser.parse_args()

    manage_parameter_store(
        region=args.region,
        prefix=args.prefix,
        recursive=args.recursive,
        force=args.force,
        dry_run=args.dry_run,
    )
