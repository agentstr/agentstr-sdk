import boto3
import botocore
import argparse

def manage_secrets(region):
    """Lists all secrets in AWS Secrets Manager and provides an option to delete them interactively."""
    try:
        # It's recommended to configure your AWS region.
        # You can pass it to the client, e.g., boto3.client('secretsmanager', region_name='us-east-1')
        # Or configure it via environment variables (AWS_REGION) or ~/.aws/config
        client = boto3.client('secretsmanager', region_name=region)

        region_name = region if region else client.meta.region_name
        print(f"Fetching all secrets from AWS Secrets Manager in region: {region_name}...")

        secrets_to_delete = []
        paginator = client.get_paginator('list_secrets')
        page_iterator = paginator.paginate()

        for page in page_iterator:
            for secret in page['SecretList']:
                secrets_to_delete.append(secret['ARN'])
                print(f"  - Found secret: {secret['Name']} (ARN: {secret['ARN']})")

        if not secrets_to_delete:
            print("No secrets found.")
            return

        print(f"\nFound a total of {len(secrets_to_delete)} secrets.")

        # Ask for confirmation before proceeding with deletion
        proceed = input("Do you want to proceed with deleting secrets? (yes/no): ").lower()
        if proceed != 'yes':
            print("Aborting. No secrets will be deleted.")
            return

        for secret_arn in secrets_to_delete:
            try:
                # Confirm deletion for each secret
            
                print(f"Deleting secret: {secret_arn}")
                # By default, secrets are not deleted immediately. 
                # They are scheduled for deletion after a recovery window of 7 to 30 days.
                # To force immediate deletion without recovery, use ForceDeleteWithoutRecovery=True
                client.delete_secret(
                    SecretId=secret_arn,
                    RecoveryWindowInDays=7  # Set a recovery window (minimum 7 days)
                    # ForceDeleteWithoutRecovery=True # Uncomment for immediate, irreversible deletion
                )
                print(f"Successfully scheduled secret {secret_arn} for deletion.")
            except botocore.exceptions.ClientError as e:
                print(f"Error deleting secret {secret_arn}: {e}")

        print("\nSecret management process finished.")

    except botocore.exceptions.NoCredentialsError:
        print("AWS credentials not found. Please configure your credentials.")
    except botocore.exceptions.ClientError as e:
        print(f"An AWS client error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List and delete secrets from AWS Secrets Manager.')
    parser.add_argument('--region', type=str, help='The AWS region to use. If not specified, the default region will be used.')
    args = parser.parse_args()
    manage_secrets(region=args.region)
