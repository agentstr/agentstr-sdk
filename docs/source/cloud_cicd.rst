Cloud & CI/CD
=============

The Agentstr SDK provides a powerful command-line interface (CLI) to deploy your agents to the cloud with minimal configuration. This guide covers how to deploy to AWS, Google Cloud, and Azure, and set up automated CI/CD pipelines with GitHub Actions.

.. note::
   The ``agentstr`` CLI is designed to abstract away the complexities of cloud infrastructure. You don't need to write any Terraform or CloudFormation templates.

Prerequisites
-------------

Before you can deploy, make sure you have the following tools installed and configured:

*   **Docker:** Required for building and containerizing your agent.
*   **Cloud-specific CLIs:**
    *   **AWS:** `AWS CLI <https://aws.amazon.com/cli/>`_
    *   **Google Cloud:** `gcloud CLI <https://cloud.google.com/sdk/gcloud>`_ and `kubectl <https://kubernetes.io/docs/tasks/tools/install-kubectl/>`_
    *   **Azure:** `Azure CLI <https://docs.microsoft.com/en-us/cli/azure/install-azure-cli>`_

You must also be authenticated with your chosen cloud provider and have permissions to push to its container registry (e.g., ECR, GCR, ACR).

Configuration File
------------------

All deployment commands are driven by a YAML configuration file. This file tells the CLI which provider to use, where your agent's code is, and how to configure the deployment.

Here is an example of a complete configuration file:

.. code-block:: yaml
   :caption: config.yaml

   # Cloud provider: aws, gcp, or azure
   provider: aws

   # Path to your agent's main Python file
   file_path: app/agent.py

   # Name for your deployment/service (optional)
   name: my-awesome-agent

   # Resource allocation (optional)
   cpu: 256          # CPU units (AWS/Azure) or cores (GCP)
   memory: 512       # Memory in MiB

   # Extra PyPI packages to install (optional)
   extra_pip_deps:
     - openai
     - langchain

   # Environment variables for your agent (optional)
   env:
     MY_API_KEY: "some_value"

   # References to secrets managed by your cloud provider (optional)
   secrets:
     MY_SECRET: arn:aws:secretsmanager:us-west-2:123456789012:secret:my-secret-AbCdEf

.. tip::
   You can pass the configuration file to any command using the ``-f`` or ``--config`` flag. Alternatively, set the ``AGENTSTR_CONFIG`` environment variable.

CLI Commands
------------

Once your configuration file is ready, you can use the following commands to manage your deployment.

**Deploy or Update an Agent**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``deploy`` command builds a Docker image of your agent, pushes it to your cloud provider's registry, and deploys it as a service.

.. code-block:: bash

   agentstr deploy -f path/to/config.yaml

**View Agent Logs**
^^^^^^^^^^^^^^^^^^^

To stream logs from your running agent, use the ``logs`` command:

.. code-block:: bash

   agentstr logs -f path/to/config.yaml

**List Deployments**
^^^^^^^^^^^^^^^^^^^^

You can list all active agent deployments managed by the CLI:

.. code-block:: bash

   agentstr list -f path/to/config.yaml

**Destroy a Deployment**
^^^^^^^^^^^^^^^^^^^^^^^^

To tear down a deployment and delete all associated resources, use the ``destroy`` command:

.. code-block:: bash

   agentstr destroy -f path/to/config.yaml

CI/CD with GitHub Actions
-------------------------

The Agentstr SDK includes ready-to-use GitHub Actions workflows to automate your deployments. On every push to your repository, these workflows can build and deploy your agent to the cloud.

To get started, copy one of the following workflow files into the ``.github/workflows/`` directory of your repository and configure the required secrets in your GitHub project settings.

.. list-table:: Available Workflows
   :header-rows: 1
   :widths: 10 20 40

   * - Cloud
     - Workflow File
     - Description
   * - AWS
     - `deploy-aws.yml <https://github.com/agentstr/agentstr-sdk/blob/main/.github/workflows/deploy-aws.yml>`_
     - Authenticates with AWS and runs ``agentstr deploy``.
   * - GCP
     - `deploy-gcp.yml <https://github.com/agentstr/agentstr-sdk/blob/main/.github/workflows/deploy-gcp.yml>`_
     - Authenticates with a GCP service account and runs ``agentstr deploy``.
   * - Azure
     - `deploy-azure.yml <https://github.com/agentstr/agentstr-sdk/blob/main/.github/workflows/deploy-azure.yml>`_
     - Logs in with the Azure CLI and runs ``agentstr deploy``.

**Workflow Examples**

For reference, here are the contents of the workflow files.

**AWS**

.. code-block:: yaml
   :linenos:

   # GitHub Actions workflow: Deploy to AWS with agentstr-cli

   name: deploy-aws

   # Trigger manually or when the AWS config changes
   on:
     workflow_dispatch:
     push:
       branches:
         - main
       paths:
         - "configs/aws.yml"
         - ".github/workflows/deploy-aws.yml"

   jobs:
     deploy:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v4

         - name: Install uv
           uses: astral-sh/setup-uv@v5

         - name: "Set up Python"
           uses: actions/setup-python@v5
           with:
             python-version-file: ".python-version"
             
         - name: Install the project
           run: uv sync --all-extras --dev

         - name: Deploy to AWS
           env:
             AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
             AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
             AWS_DEFAULT_REGION: ${{ secrets.AWS_REGION }}
           run: uv run agentstr deploy -f configs/aws.yml

**GCP**

.. code-block:: yaml
   :linenos:

   # GitHub Actions workflow: Deploy to Google Cloud Run with agentstr-cli

   name: deploy-gcp

   on:
     workflow_dispatch:
     push:
       branches:
         - main
       paths:
         - "configs/gcp.yml"
         - ".github/workflows/deploy-gcp.yml"

   jobs:
     deploy:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v4

         - name: Install uv
           uses: astral-sh/setup-uv@v5

         - name: "Set up Python"
           uses: actions/setup-python@v5
           with:
             python-version-file: ".python-version"

         - name: Install the project
           run: uv sync --all-extras --dev

         - name: Authenticate to GCP
           uses: google-github-actions/auth@v2
           with:
             credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

         # Get the GKE credentials so we can deploy to the cluster
         - uses: google-github-actions/get-gke-credentials@db150f2cc60d1716e61922b832eae71d2a45938f
           with:
             cluster_name: agentstr-cluster
             location: us-central1-b
             credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

         - name: Install gke-gcloud-auth-plugin
           uses: simenandre/setup-gke-gcloud-auth-plugin@v1 # Or the latest version

         - name: Deploy to GCP
           env:
             GCP_PROJECT: ${{ secrets.GCP_PROJECT }}
           run: uv run agentstr deploy -f configs/gcp.yml

**Azure**

.. code-block:: yaml
   :linenos:

   # GitHub Actions workflow: Deploy to Azure Container Instances with agentstr-cli

   name: deploy-azure

   on:
     workflow_dispatch:
     push:
       branches:
         - main
       paths:
         - "configs/azure.yml"
         - ".github/workflows/deploy-azure.yml"

   jobs:
     deploy:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v4

         - name: Install uv
           uses: astral-sh/setup-uv@v5

         - name: "Set up Python"
           uses: actions/setup-python@v5
           with:
             python-version-file: ".python-version"

         - name: Install the project
           run: uv sync --all-extras --dev

         - name: Azure Login
           uses: azure/login@v2
           with:
             creds: ${{ secrets.AZURE_CREDENTIALS }}

         - name: Deploy to Azure
           env:
             AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
           run: uv run agentstr deploy -f configs/azure.yml

