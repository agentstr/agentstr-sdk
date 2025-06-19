Agentstr CLI
============

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

Installation
------------
The CLI is installed automatically when you install the SDK with the *cli*
extra:

.. code-block:: bash

   uv add agentstr-sdk[cli]   # or: pip install "agentstr-sdk[cli]"

This places an ``agentstr`` executable on your ``$PATH``.

Using a config file
--------------

.. list-table::
   :header-rows: 1

   * - Option
     - Description
     - Default
   * - ``--provider`` ``aws|gcp|azure``
     - Target cloud provider.
     - ``AGENTSTR_PROVIDER`` env-var, otherwise inferred from config or ``aws``
   * - ``-f``, ``--config`` *PATH*
     - YAML config file (can also use ``AGENTSTR_CONFIG``).
     - –
   * - ``-h``, ``--help``
     - Show contextual help.
     - –

 ``provider:`` key, the CLI will automatically infer the cloud, so you normally only need to reference the config file.

Basic commands
--------------

Once your YAML is ready you can:

.. code-block:: bash

   agentstr deploy -f configs/aws.yml      # create / update
   agentstr logs -f configs/aws.yml        # live logs
   agentstr destroy -f configs/aws.yml     # tear down

     - Purpose
   * - ``deploy <app.py>``
     - Build Docker image, push and deploy *app.py* as a container service.
   * - ``put-secret <key> <value>``
     - Create or update a single secret and print its reference.
   * - ``put-secrets <env_file>``
     - Create or update multiple secrets from a .env file.
   * - ``list``
     - List existing deployments.
   * - ``logs <name>``
     - Stream recent logs from a deployment.
   * - ``destroy <name>``
     - Tear down the deployment/service.


------------------

.. list-table::
   :header-rows: 1

   * - Option
     - Description
     - Default
   * - ``--name`` *STRING*
     - Override deployment name (defaults to filename stem).
     - ``<app>``
   * - ``--cpu`` *INT*
     - CPU units (AWS) / cores (GCP/Azure).
     - ``256`` (AWS) / ``0.25`` (GCP/Azure)
   * - ``--memory`` *INT*
     - Memory in MiB.
     - ``512``
   * - ``--env`` *KEY=VAL* (repeat)
     - Add environment variables passed to the container.
     - –
   * - ``--pip`` *PACKAGE* (repeat)
     - Extra Python dependencies installed into the image.
     - –
   * - ``--secret`` *KEY=VAL* (repeat)
     - Secrets are pulled from cloud provider's secret manager.
     - –

Config files (``configs/`` folder)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


.. code-block:: bash
  
  # Deploy / update
  agentstr deploy -f configs/aws.yml

  # View logs
  agentstr logs -f configs/aws.yml

  # Destroy
  agentstr destroy -f configs/aws.yml

Config reference
-------------------------
The repository ships with ready-made workflows to deploy your agent to **AWS**, **GCP** or **Azure** on every push. Copy the desired file, set the required secrets and you are ready to _push-to-deploy_.

.. list-table::
   :header-rows: 1
   :widths: 10 20 40

   * - Cloud
     - Workflow file
     - Purpose
   * - AWS
     - :file:`.github/workflows/deploy-aws.yml`
     - Installs dependencies, authenticates with AWS and runs ``agentstr deploy -f configs/aws.yml``.
   * - GCP
     - :file:`.github/workflows/deploy-gcp.yml`
     - Authenticates with a service-account key, installs ``kubectl`` / GKE plugin and deploys using ``configs/gcp.yml``.
   * - Azure
     - :file:`.github/workflows/deploy-azure.yml`
     - Logs in with ``az`` and deploys using ``configs/azure.yml``.

Below are the workflow definitions for reference:

.. tabs::

   .. tab:: AWS

      .. literalinclude:: ../../.github/workflows/deploy-aws.yml
         :language: yaml
         :linenos:

   .. tab:: GCP

      .. literalinclude:: ../../.github/workflows/deploy-gcp.yml
         :language: yaml
         :linenos:

   .. tab:: Azure

      .. literalinclude:: ../../.github/workflows/deploy-azure.yml
         :language: yaml
         :linenos:
