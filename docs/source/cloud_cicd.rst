Cloud & CI/CD
=============

The ``agentstr`` command-line tool lets you deploy a single-file Python “agent” to
AWS ECS Fargate, Google Kubernetes Engine or Azure Container Instances with **zero
infrastructure code**.

Prerequisites
-------------

You need Docker running for *all* providers.

.. list-table::
   :header-rows: 1
   :widths: 15 25 35

   * - Provider
     - CLI tools
     - Environment variables
   * - AWS
     - ``aws``
     - ``AWS_PROFILE`` *or* standard AWS credential env vars
   * - GCP
     - ``gcloud``, ``kubectl``
     - ``GCP_PROJECT``
   * - Azure
     - ``az``
     - ``AZURE_SUBSCRIPTION_ID``

Ensure each CLI is authenticated and Docker can push to the relevant registry.

Basic Commands
--------------

* - ``deploy -f path/to/config.yaml``
  - Build Docker image, push and deploy *app.py* as a container service.
* - ``list -f path/to/config.yaml``
  - List existing deployments.
* - ``logs -f path/to/config.yaml``
  - Stream recent logs from a deployment.
* - ``destroy -f path/to/config.yaml``
  - Tear down the deployment/service.

Configuration
-------------

A minimal template you can reuse across commands. Pass it *anywhere* on the command line with ``-f/--config`` or set the ``AGENTSTR_CONFIG`` env var.

.. code-block:: yaml

   provider: aws            # aws | gcp | azure
   file_path: app/agent.py  # Python entry-point
   name: my-agent           # optional – deployment name
   cpu: 256                 # optional – CPU units / cores
   memory: 512              # optional – memory in MiB
   extra_pip_deps:          # optional – extra pip packages
     - openai
     - langchain
   env:                     # optional – env vars
     MY_VAR: 123
   secrets:                 # optional – provider secret refs
     MY_SECRET: arn:aws:secretsmanager:us-west-2:123:secret:MY_SECRET

.. list-table:: Key fields
   :header-rows: 1
   :widths: 15 10 45

   * - Field
     - Type
     - Description
   * - ``provider``
     - string
     - Required. One of ``aws``, ``gcp``, ``azure``.
   * - ``file_path``
     - path
     - Required. Python file executed inside the container.
   * - ``name``
     - string
     - Deployment/service name. Defaults to filename stem.
   * - ``cpu``
     - int
     - CPU units / cores to allocate.
   * - ``memory``
     - int
     - Memory in MiB.
   * - ``env``
     - map
     - Environment variables passed to the container.
   * - ``secrets``
     - map
     - Provider-managed secret references (ARN/URI/path).
   * - ``extra_pip_deps``
     - list
     - Extra PyPI packages installed into the image before deploy.



Cloud Provider Environment Variables
------------------------------------

.. code-block:: bash

   # AWS (assuming aws is authenticated)
   export AWS_PROFILE=your-profile

   # GCP (assuming gcloud is authenticated)
   export GCP_PROJECT=your-project

   # Azure (assuming az is authenticated)
   export AZURE_SUBSCRIPTION_ID=your-subscription-id

CLI Commands
------------

.. code-block:: bash
  
  # Deploy / update
  agentstr deploy -f configs/aws.yml

  # View logs
  agentstr logs -f configs/aws.yml

  # List deployments
  agentstr list -f configs/aws.yml

  # Destroy
  agentstr destroy -f configs/aws.yml

CI/CD - GitHub Actions
----------------------
The repository ships with ready-made workflows to deploy your agent to **AWS**, **GCP** or **Azure** on every push. Copy the desired file, set the required secrets and you are ready to deploy.

.. list-table::
   :header-rows: 1
   :widths: 10 20 40

   * - Cloud
     - Workflow file
     - Purpose
   * - AWS
     - `deploy-aws.yml <https://github.com/agentstr/agentstr-sdk/blob/dev/.github/workflows/deploy-aws.yml>`_
     - Installs dependencies, authenticates with AWS and runs ``agentstr deploy -f configs/aws.yml``.
   * - GCP
     - `deploy-gcp.yml <https://github.com/agentstr/agentstr-sdk/blob/dev/.github/workflows/deploy-gcp.yml>`_
     - Authenticates with a service-account key, installs ``kubectl`` / GKE plugin and deploys using ``configs/gcp.yml``.
   * - Azure
     - `deploy-azure.yml <https://github.com/agentstr/agentstr-sdk/blob/dev/.github/workflows/deploy-azure.yml>`_
     - Logs in with ``az`` and deploys using ``configs/azure.yml``.

Below are the workflow definitions for reference:

**AWS**

.. literalinclude:: ../../.github/workflows/deploy-aws.yml
   :language: yaml
   :linenos:
    
**GCP**

.. literalinclude:: ../../.github/workflows/deploy-gcp.yml
   :language: yaml
   :linenos:

**Azure**

.. literalinclude:: ../../.github/workflows/deploy-azure.yml
   :language: yaml
   :linenos:
