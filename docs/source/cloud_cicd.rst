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

    -   **AWS:** `AWS CLI <https://aws.amazon.com/cli/>`_
    -   **Google Cloud:** `gcloud CLI <https://cloud.google.com/sdk/gcloud>`_ and `kubectl <https://kubernetes.io/docs/tasks/tools/install-kubectl/>`_
    -   **Azure:** `Azure CLI <https://docs.microsoft.com/en-us/cli/azure/install-azure-cli>`_

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

   # Database (optional but recommended for production)
   database: true

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

   # Path to a .env file for loading secrets (optional)
   env_file: .env

.. tip::
   You can pass the configuration file to any command using the ``-f`` or ``--config`` flag. Alternatively, set the ``AGENTSTR_CONFIG`` environment variable.

.. note::
   Configuration values are resolved with the following precedence (highest to lowest). If a variable is specified in multiple locations, the one with the highest precedence is used.

   1.  Direct command-line flags (e.g., ``--env`` or ``--secret``)
   2.  The ``env`` or ``secrets`` maps in the YAML configuration file
   3.  Variables defined in the ``env_file``

   Variables from the ``env_file`` and the ``secrets`` map are always treated as secrets and are uploaded to your cloud provider's secret manager. Variables from the ``env`` map and the ``--env`` flag are passed as plaintext environment variables.

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

.. note::
   For more information on the CLI commands, see the :doc:`agentstr/cli` module.

Local Docker Deployment
-----------------------

Docker deployments are ideal for local development and testing. They allow you to run Agentstr applications in isolated containers on your machine without needing cloud credentials or internet access.

**Prerequisites**:

- Docker and Docker Compose must be installed on your system.
- Ensure the Agentstr CLI is installed (``pip install agentstr-sdk[cli]``).

**Steps**:

1. **Set the provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=docker

2. **Deploy your application**:

   .. code-block:: bash

      agentstr deploy -f path/to/deploy.yml

   This will create a Docker container for your application and, if needed, a Postgres database container. Both are networked together automatically.

3. **List deployments**:

   .. code-block:: bash

      agentstr list

   You'll see only Agentstr-related containers prefixed with ``agentstr-``.

4. **View logs**:

   .. code-block:: bash

      agentstr logs -f path/to/deploy.yml

5. **Destroy the deployment** when done:

   .. code-block:: bash

      agentstr destroy -f path/to/deploy.yml

**Benefits of Docker Deployment**:

- **Isolation**: Each deployment runs in its own container, preventing dependency conflicts.
- **Consistency**: Mimics production environment setup with containers.
- **Speed**: No cloud latency or credential setup needed.
- **Cost**: Free for local development.

**Limitations**:

- Not suitable for production due to lack of scalability and persistence compared to cloud providers.
- Requires local Docker setup and resources.

.. note::
   If you encounter connection issues between your application and database, ensure both containers are running and on the same network. The Agentstr CLI handles this automatically, but manual Docker inspection can confirm (``docker ps``, ``docker network ls``).

Nostr Metadata
--------------

When deploying your Agentstr application to the cloud, if you have a ``nostr-metadata.yml`` file in the same directory as your main application file, it will be automatically deployed along with your application. This file contains metadata for your application's Nostr profile, which will be used by the Agentstr SDK to update and broadcast your profile information on the Nostr network.

For more information on Nostr metadata and how to configure it, refer to :doc:`key_concepts/nostr_metadata`.

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
     - `deploy-aws.yml <https://github.com/agentstr/agentstr-sdk/blob/main/workflows/deploy-aws.template.yml>`_
     - Authenticates with AWS and runs ``agentstr deploy``.
   * - GCP
     - `deploy-gcp.yml <https://github.com/agentstr/agentstr-sdk/blob/main/workflows/deploy-gcp.template.yml>`_
     - Authenticates with a GCP service account and runs ``agentstr deploy``.
   * - Azure
     - `deploy-azure.yml <https://github.com/agentstr/agentstr-sdk/blob/main/workflows/deploy-azure.template.yml>`_
     - Logs in with Azure credentials and runs ``agentstr deploy``.

.. list-table:: Required Secrets
   :header-rows: 1
   :widths: 10 20 40

   * - Cloud
     - Secret Name
     - Description
   * - AWS
     - ``AWS_ACCESS_KEY_ID``, ``AWS_SECRET_ACCESS_KEY``, ``AWS_REGION``
     - AWS credentials and region for authentication.
   * - GCP
     - ``GCP_PROJECT``, ``GCP_SERVICE_ACCOUNT_KEY``
     - GCP project ID and service account key for authentication.
   * - Azure
     - ``AZURE_SUBSCRIPTION_ID``, ``AZURE_CREDENTIALS``
     - Azure subscription ID and credentials for authentication.


**Workflow Examples**

For reference, here are the contents of the workflow files. Make sure to update the `AGENTSTR_CONFIG` environment variable to point to your Agentstr configuration file.

**AWS**

.. literalinclude:: ../../workflows/deploy-aws.template.yml
   :language: yaml
   :linenos:

**GCP**

.. literalinclude:: ../../workflows/deploy-gcp.template.yml
   :language: yaml
   :linenos:

**Azure**

.. literalinclude:: ../../workflows/deploy-azure.template.yml
   :language: yaml
   :linenos: