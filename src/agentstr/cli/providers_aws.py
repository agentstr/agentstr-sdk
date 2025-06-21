"""AWS provider implementation extracted from providers.py."""
from __future__ import annotations

import sys
from botocore.exceptions import ClientError
import subprocess
import tempfile
import uuid
import base64
import secrets
import json
import os
from pathlib import Path
from typing import Dict, Optional, List

import click

from .providers import _catch_exceptions, register_provider, Provider  # type: ignore


@register_provider("aws")
class AWSProvider(Provider):  # noqa: D401
    """AWS ECS Fargate implementation using boto3 and Docker CLI."""

    CLUSTER_NAME = "agentstr-cluster"
    ECR_REPO_NAME = "agentstr"

    def __init__(self) -> None:  # noqa: D401
        super().__init__("aws")
        try:
            import boto3  # noqa: WPS433 (dynamic import)
        except ImportError as exc:  # pragma: no cover
            click.echo("boto3 is required for AWS provider. Please install with 'pip install boto3'", err=True)
            raise exc
        self.boto3 = sys.modules["boto3"]
        session = self.boto3.session.Session()
        # Explicit env-var check first
        if not (
            os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")
        ) and not os.getenv("AWS_PROFILE"):
            raise click.ClickException(
                "AWS credentials not found. Set AWS_ACCESS_KEY_ID/SECRET_ACCESS_KEY or AWS_PROFILE."
            )
        creds = session.get_credentials()
        if creds is None or creds.access_key is None:
            raise click.ClickException("AWS credentials could not be resolved by boto3.")
        # Determine region (fallback to us-east-1)
        region = session.region_name or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
        self.ecs = self.boto3.client("ecs", region_name=region)
        self.ecr = self.boto3.client("ecr", region_name=region)
        self.iam = self.boto3.client("iam", region_name=region)
        self.logs_client = self.boto3.client("logs", region_name=region)
        self.ec2 = self.boto3.client("ec2", region_name=region)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _run_cmd(self, cmd: List[str]):  # noqa: D401
        """Run shell command and stream output, raises on failure."""
        click.echo(" ".join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert proc.stdout
        for line in proc.stdout:
            click.echo(line.rstrip())
        proc.wait()
        if proc.returncode != 0:
            raise click.ClickException(f"Command {' '.join(cmd)} failed with code {proc.returncode}")

    # ECR ----------------------------------------------------------------
    def _ensure_ecr_repo(self) -> str:  # noqa: D401
        try:
            self.ecr.create_repository(repositoryName=self.ECR_REPO_NAME)
        except self.ecr.exceptions.RepositoryAlreadyExistsException:
            pass
        repo = self.ecr.describe_repositories(repositoryNames=[self.ECR_REPO_NAME])["repositories"][0]
        return repo["repositoryUri"]

    # IAM ----------------------------------------------------------------
    def _ensure_role(self, name: str, *, assume_policy: str, policies: list[str]) -> str:  # noqa: D401
        try:
            role = self.iam.get_role(RoleName=name)["Role"]
        except self.iam.exceptions.NoSuchEntityException:
            role = self.iam.create_role(RoleName=name, AssumeRolePolicyDocument=assume_policy)["Role"]
        for pol in policies:
            try:
                self.iam.attach_role_policy(RoleName=name, PolicyArn=pol)
            except self.iam.exceptions.EntityAlreadyExistsException:
                pass
        return role["Arn"]

    def _ensure_task_roles(self, *, deployment_name: str, secret_arns: list[str] | None = None):  # noqa: D401
        # Create a unique task role per deployment for least-privilege secrets access
        role_name = f"agentstrEcsTaskRole-{deployment_name}"
        execution_role_name = f"agentstrEcsTaskExecutionRole-{deployment_name}"
        assume_policy_dict = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        # Always attach the basic ECS execution role to the execution role
        exec_role_arn = self._ensure_role(
            execution_role_name,
            assume_policy=json.dumps(assume_policy_dict),
            policies=["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"],
        )
        task_role_arn = self._ensure_role(
            role_name,
            assume_policy=json.dumps(assume_policy_dict),
            policies=["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"],
        )
        if secret_arns:
            stmt = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["secretsmanager:GetSecretValue"],
                        "Resource": [f"{secret}-??????" for secret in secret_arns],
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["kms:Decrypt"],
                        "Resource": "*"
                    }
                ],
            }
            try:
                self.iam.put_role_policy(
                    RoleName=role_name,
                    PolicyName=f"AgentstrSecretsAccess-{role_name}",
                    PolicyDocument=json.dumps(stmt),
                )
                self.iam.put_role_policy(
                    RoleName=execution_role_name,
                    PolicyName=f"AgentstrSecretsAccess-{execution_role_name}",
                    PolicyDocument=json.dumps(stmt),
                )
            except self.iam.exceptions.MalformedPolicyDocumentException as exc:  # pragma: no cover
                click.echo(f"Failed attaching secret policy: {exc}", err=True)
        return task_role_arn, exec_role_arn

    # ECS network --------------------------------------------------------
    def _default_network(self):  # noqa: D401
        vpcs = self.ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])["Vpcs"]
        if not vpcs:
            raise click.ClickException("No default VPC found; specify network details manually.")
        vpc_id = vpcs[0]["VpcId"]
        subnets = self.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]
        # Prefer public subnets (MapPublicIpOnLaunch == True)
        public_subnets = [s for s in subnets if s.get("MapPublicIpOnLaunch")]
        if public_subnets:
            subnet_ids = [s["SubnetId"] for s in public_subnets]
        else:
            subnet_ids = [s["SubnetId"] for s in subnets]
        sg_id = self.ec2.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": ["default"]}, {"Name": "vpc-id", "Values": [vpc_id]}]
        )["SecurityGroups"][0]["GroupId"]
        return subnet_ids, [sg_id]

    # Log group ----------------------------------------------------------
    def _ensure_log_group(self, deployment_name: str):  # noqa: D401
        import time

        log_group = f"/ecs/{deployment_name}"
        groups = self.logs_client.describe_log_groups(logGroupNamePrefix=log_group, limit=1).get("logGroups", [])
        if not groups:
            try:
                self.logs_client.create_log_group(logGroupName=log_group)
            except self.logs_client.exceptions.ResourceAlreadyExistsException:
                pass
        for _ in range(5):
            groups = self.logs_client.describe_log_groups(logGroupNamePrefix=log_group, limit=1).get("logGroups", [])
            if groups:
                return
            time.sleep(1)

    # Build & push image --------------------------------------------------
    def _build_and_push_image(self, file_path: Path, deployment_name: str, dependencies: list[str]) -> str:  # noqa: D401
        repo_uri = self._ensure_ecr_repo()
        image_tag = uuid.uuid4().hex[:8]
        image_uri = f"{repo_uri}:{image_tag}"

        with tempfile.TemporaryDirectory() as tmp_dir:
            dockerfile_path = Path(tmp_dir) / "Dockerfile"
            deps_line = " " + " ".join(dependencies) if dependencies else ""
            if "agentstr-sdk" not in deps_line:
                deps_line = "agentstr-sdk[all] " + deps_line
            dockerfile_path.write_text(
                f"""
FROM public.ecr.aws/docker/library/python:3.12-slim
WORKDIR /app
COPY app.py /app/app.py
RUN pip install --no-cache-dir {deps_line}
CMD [\"python\", \"/app/app.py\"]
"""
            )
            temp_app = Path(tmp_dir) / "app.py"
            temp_app.write_text(file_path.read_text())
            self._run_cmd(["docker", "build", "-t", image_uri, tmp_dir])
            auth = self.ecr.get_authorization_token()["authorizationData"][0]
            b64_token = auth["authorizationToken"]
            user_pass = base64.b64decode(b64_token).decode()
            password = user_pass.split(":", 1)[1]
            registry = auth["proxyEndpoint"].replace("https://", "")
            self._run_cmd(["docker", "login", "-u", "AWS", "-p", password, registry])
            self._run_cmd(["docker", "push", image_uri])
        return image_uri

    # Task definition -----------------------------------------------------
    def _register_task_definition(
        self,
        deployment_name: str,
        image_uri: str,
        exec_role_arn: str,
        task_role_arn: str,
        env_vars: Dict[str, str],
        secrets: Dict[str, str],
        cpu: int,
        memory: int,
    ) -> str:  # noqa: D401
        env_list = [{"name": k, "value": v} for k, v in env_vars.items()]
        secret_list = [{"name": k, "valueFrom": v} for k, v in secrets.items()]
        container_def = {
            "name": deployment_name,
            "image": image_uri,
            "essential": True,
            "memory": memory,
            "cpu": cpu,
            "environment": env_list,
            "secrets": secret_list,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": f"/ecs/{deployment_name}",
                    "awslogs-region": self.ecs.meta.region_name,
                    "awslogs-stream-prefix": "ecs",
                },
            },
        }
        resp = self.ecs.register_task_definition(
            family=deployment_name,
            taskRoleArn=task_role_arn,
            executionRoleArn=exec_role_arn,
            networkMode="awsvpc",
            requiresCompatibilities=["FARGATE"],
            cpu=str(cpu),
            memory=str(memory),
            containerDefinitions=[container_def],
        )
        return resp["taskDefinition"]["taskDefinitionArn"]

    def _ensure_cluster(self, *, create_if_missing: bool = True) -> str | None:  # noqa: D401
        clusters = self.ecs.list_clusters()["clusterArns"]
        cluster_arn: Optional[str] = None
        for arn in clusters:
            if arn.split("/")[-1] == self.CLUSTER_NAME:
                cluster_arn = arn
                break
        if not cluster_arn and create_if_missing:
            cluster_arn = self.ecs.create_cluster(clusterName=self.CLUSTER_NAME)["cluster"]["clusterArn"]
        return cluster_arn

    def _create_service(self, cluster_arn: str, deployment_name: str, task_def_arn: str):  # noqa: D401
        """Create or update ECS service safely.

        If a service exists but is not ACTIVE, we delete and recreate it to
        avoid ServiceNotActiveException.
        """
        subnet_ids, sg_ids = self._default_network()

        # Helper: create or recreate service
        def _create():
            click.echo("Creating ECS service ...")
            self.ecs.create_service(
                cluster=self.CLUSTER_NAME,
                serviceName=deployment_name,
                taskDefinition=task_def_arn,
                desiredCount=1,
                launchType="FARGATE",
                networkConfiguration={
                    "awsvpcConfiguration": {
                        "subnets": subnet_ids,
                        "securityGroups": sg_ids,
                        "assignPublicIp": "ENABLED",
                    }
                },
            )

        # Helper: recreate service (delete + create)
        def _recreate():
            # Delete and recreate
            try:
                self.ecs.update_service(cluster=self.CLUSTER_NAME, service=deployment_name, desiredCount=0)
            except ClientError as exc:
                if exc.response.get("Error", {}).get("Code") != "ServiceNotActiveException":
                    raise  # unexpected
            except self.ecs.exceptions.ServiceNotActiveException:
                pass  # already inactive
            try:
                self.ecs.delete_service(cluster=self.CLUSTER_NAME, service=deployment_name, force=True)
            except self.ecs.exceptions.ServiceNotFoundException:
                pass
            # Wait until service is fully inactive
            try:
                waiter = self.ecs.get_waiter("services_inactive")
                waiter.wait(cluster=self.CLUSTER_NAME, services=[deployment_name])
            except Exception:  # pragma: no cover
                pass
            _create()

        try:
            resp = self.ecs.describe_services(cluster=self.CLUSTER_NAME, services=[deployment_name])
            services = resp.get("services", [])
            if not services:
                # Service not found – create new
                _create()
            else:
                svc = services[0]
                status = svc.get("status")
                if status != "ACTIVE":
                    click.echo(f"Service exists but is not ACTIVE (status={status}); deleting and recreating ...")
                    _recreate()
                else:
                    # Update service in-place to use new task definition
                    click.echo("Service already exists and is ACTIVE; updating in place ...")
                    self.ecs.update_service(
                        cluster=self.CLUSTER_NAME,
                        service=deployment_name,
                        taskDefinition=task_def_arn,
                        desiredCount=1,
                        networkConfiguration={
                            "awsvpcConfiguration": {
                                "subnets": subnet_ids,
                                "securityGroups": sg_ids,
                                "assignPublicIp": "ENABLED",
                            }
                        },
                    )
        except self.ecs.exceptions.ServiceNotFoundException:
            _create()
        return

    # ------------------------------------------------------------------
    # Public Provider interface
    # ------------------------------------------------------------------

    @_catch_exceptions
    def deploy(self, file_path: Path, deployment_name: str, *, secrets: Dict[str, str], **kwargs):  # noqa: D401
        env = kwargs.get("env", {})
        dependencies = kwargs.get("dependencies", [])
        cpu = int(kwargs.get("cpu", 256))
        memory = int(kwargs.get("memory", 512))
        click.echo(
            f"[AWS] Deploying {file_path} as '{deployment_name}' (cpu={cpu}, memory={memory}, deps={dependencies}) ..."
        )
        image_uri = self._build_and_push_image(file_path, deployment_name, dependencies)
        cluster_arn = self._ensure_cluster()
        # Only pass ARNs that look like SecretsManager ARNs
        secret_arns = [v for v in secrets.values() if v.startswith("arn:aws:secretsmanager:")]
        task_role_arn, exec_role_arn = self._ensure_task_roles(deployment_name=deployment_name, secret_arns=secret_arns)
        task_def_arn = self._register_task_definition(
            deployment_name,
            image_uri,
            exec_role_arn,
            task_role_arn,
            env,
            secrets,
            cpu,
            memory,
        )
        self._ensure_log_group(deployment_name)
        self._create_service(cluster_arn, deployment_name, task_def_arn)
        click.echo("Deployment successful. Service is starting (may take ~1-2 min).")

    @_catch_exceptions
    def list(self, *, name_filter: Optional[str] = None):  # noqa: D401
        cluster_arn = self._ensure_cluster(create_if_missing=False)
        if not cluster_arn:
            click.echo("No cluster found.")
            return
        srv_arns: List[str] = []
        paginator = self.ecs.get_paginator("list_services")
        for page in paginator.paginate(cluster=self.CLUSTER_NAME):
            srv_arns.extend(page.get("serviceArns", []))
        if not srv_arns:
            click.echo("No services found.")
            return
        services = self.ecs.describe_services(cluster=self.CLUSTER_NAME, services=srv_arns)["services"]
        for svc in services:
            name = svc["serviceName"]
            if name_filter and name_filter not in name:
                continue
            status = svc["status"]
            desired = svc["desiredCount"]
            running = svc["runningCount"]
            click.echo(f"{name} – status: {status}, desired: {desired}, running: {running}")

    @_catch_exceptions
    def logs(self, deployment_name: str):  # noqa: D401
        """Fetch and stream recent log events with a short wait for task start."""
        import time

        log_group = f"/ecs/{deployment_name}"
        wait_seconds = 30
        poll_interval = 2
        elapsed = 0
        while elapsed <= wait_seconds:
            try:
                streams_resp = self.logs_client.describe_log_streams(
                    logGroupName=log_group,
                    orderBy="LastEventTime",
                    descending=True,
                    limit=1,
                )
                streams = streams_resp.get("logStreams", [])
                if streams:
                    stream_name = streams[0]["logStreamName"]
                    events = self.logs_client.get_log_events(
                        logGroupName=log_group,
                        logStreamName=stream_name,
                    )
                    if events.get("events"):
                        for event in events["events"]:
                            click.echo(event["message"])
                        return
            except self.logs_client.exceptions.ResourceNotFoundException:
                pass
            if elapsed == 0:
                click.echo("Waiting for logs ... (up to 30s)")
            time.sleep(poll_interval)
            elapsed += poll_interval
        click.echo("No logs available yet; the service may still be starting or not producing output.")

    @_catch_exceptions
    def put_secret(self, name: str, value: str) -> str:  # noqa: D401
        sm = self.boto3.client("secretsmanager")
        try:
            resp = sm.create_secret(Name=name, SecretString=value)
            arn = resp["ARN"]
            click.echo(f"Secret '{name}' created in Secrets Manager.")
        except sm.exceptions.ResourceExistsException:
            resp = sm.put_secret_value(SecretId=name, SecretString=value)
            arn = resp["ARN"]
            click.echo(f"Secret '{name}' updated in Secrets Manager.")
        return arn

    @_catch_exceptions
    def get_secret(self, name: str) -> str:  # noqa: D401
        sm = self.boto3.client("secretsmanager")
        resp = sm.get_secret_value(SecretId=name)
        return resp["SecretString"]

    @_catch_exceptions
    def provision_database(self, deployment_name: str) -> tuple[str, str]:  # noqa: D401
        """Provision an RDS PostgreSQL instance and store DATABASE_URL secret.

        This creates a minimal t3.micro Postgres instance (free-tier eligible in
        many regions). It waits until the instance is available and then stores
        the connection string in Secrets Manager, returning the secret ARN.
        """
        rds = self.boto3.client("rds", region_name=self.ecs.meta.region_name)
        # ------------------------------------------------------------------
        # Build a valid RDS identifier: letters, digits, hyphens; start with letter
        # ------------------------------------------------------------------
        db_id = os.getenv("DATABASE_INSTANCE_ID", "agentstr")
        master_user = "agentuser"
        password = secrets.token_urlsafe(24)
        try:
            rds.describe_db_instances(DBInstanceIdentifier=db_id)
            click.echo("RDS instance already exists – reusing.")
            try:
                secret_resp = self.boto3.client("secretsmanager").get_secret_value(SecretId=f"agentstr/DATABASE_URL")
                return "DATABASE_URL", secret_resp["ARN"]
            except self.boto3.client("secretsmanager").exceptions.ResourceNotFoundException:
                click.echo("Secret missing; generating new credentials and updating master password ...")
                # Reset master password
                rds.modify_db_instance(
                    DBInstanceIdentifier=db_id,
                    MasterUserPassword=password,
                    ApplyImmediately=True,
                )
        except rds.exceptions.DBInstanceNotFoundFault:
            click.echo("Creating Postgres (RDS) instance – this may take several minutes ...")
            rds.create_db_instance(
                DBInstanceIdentifier=db_id,
                AllocatedStorage=20,
                DBInstanceClass="db.t3.micro",
                Engine="postgres",
                MasterUsername=master_user,
                MasterUserPassword=password,
                PubliclyAccessible=True,
                StorageEncrypted=True,
                BackupRetentionPeriod=0,
            )
        waiter = rds.get_waiter("db_instance_available")
        waiter.wait(DBInstanceIdentifier=db_id)
        # Build or update secret now that endpoint is ready
        inst = rds.describe_db_instances(DBInstanceIdentifier=db_id)["DBInstances"][0]
        endpoint = inst["Endpoint"]["Address"]
        conn = f"postgresql://{master_user}:{password}@{endpoint}:5432/postgres"
        secret_name = f"agentstr/DATABASE_URL"
        secret_arn = self.put_secret(secret_name, conn)
        click.echo("Postgres ready and secret stored.")
        return "DATABASE_URL", secret_arn

    def destroy(self, deployment_name: str):  # noqa: D401
        click.echo(f"[AWS] Destroying {deployment_name} ...")
        try:
            self.ecs.update_service(cluster=self.CLUSTER_NAME, service=deployment_name, desiredCount=0)
            self.ecs.delete_service(cluster=self.CLUSTER_NAME, service=deployment_name, force=True)
            click.echo("Service deleted. Remember to deregister task definitions/ECR images manually if desired.")
        except self.ecs.exceptions.ServiceNotFoundException:
            click.echo("Service not found.")
