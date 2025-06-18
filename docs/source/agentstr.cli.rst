Agentstr CLI
============

The ``agentstr`` command-line tool lets you deploy a single-file Python “agent” to
AWS ECS Fargate, Google Kubernetes Engine or Azure Container Instances with **zero
infrastructure code**.

Installation
------------
The CLI is installed automatically when you install the SDK with the *cli*
extra:

.. code-block:: bash

   uv add agentstr-sdk[cli]   # or: pip install "agentstr-sdk[cli]"

This places an ``agentstr`` executable on your ``$PATH``.

Global options
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

If your YAML config contains a top-level ``provider:`` key, the CLI will automatically infer the cloud, so you normally only need to reference the config file.

To avoid passing flags every time, you can export environment variables:

.. code-block:: bash

   export AGENTSTR_PROVIDER=gcp  # optional when provider in config
   export AGENTSTR_CONFIG=configs/gcp.yml

Commands
--------

.. list-table::
   :header-rows: 1

   * - Command
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

``deploy`` options
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

Config files
~~~~~~~~~~~~
A YAML file lets you declare most options once and reuse them across commands. Pass it *anywhere* on the command line with ``-f/--config`` or set the ``AGENTSTR_CONFIG`` env var.

.. code-block:: bash

   agentstr -f configs/azure.yml deploy
   agentstr deploy --config configs/azure.yml
   AGENTSTR_CONFIG=configs/azure.yml agentstr deploy

Examples
~~~~~~~~

.. code-block:: bash
  
   # Deploy an agent with extra deps and environment variables to AWS (default)
   agentstr deploy my_agent.py \
       --env OPENAI_API_KEY=$OPENAI_API_KEY \
       --pip openai langchain

   # Upsert secrets from .env file
   agentstr put-secrets path/to/.env
 
   # Change provider per command
   agentstr deploy bot.py --provider gcp --cpu 2 --memory 1024

   # View logs
   agentstr logs bot

   # Destroy
   agentstr destroy bot
