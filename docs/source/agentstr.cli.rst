Agentstr CLI
============

The ``agentstr`` command-line tool lets you deploy a single-file Python “agent” to
AWS ECS Fargate, Google Kubernetes Engine or Azure Container Instances with **zero
infrastructure code**.

Installation
------------
The CLI is installed automatically when you install the SDK with the *all*
extra:

.. code-block:: bash

   uv add agentstr-sdk[all]   # or: pip install "agentstr-sdk[all]"

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
     - ``AGENTSTR_PROVIDER`` env-var, otherwise ``aws``
   * - ``-h``, ``--help``
     - Show contextual help.
     - –

To avoid passing ``--provider`` every time:

.. code-block:: bash

   export AGENTSTR_PROVIDER=gcp

Commands
--------

.. list-table::
   :header-rows: 1

   * - Command
     - Purpose
   * - ``deploy <app.py>``
     - Build Docker image, push and deploy *app.py* as a container service.
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
     - CPU units (AWS) / cores (GCP).
     - ``256`` (AWS) / ``1`` (GCP)
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
     - Secrets (merged with ``--env`` but hidden from logs).
     - –

Examples
~~~~~~~~

.. code-block:: bash

   # Deploy an agent with extra deps and environment variables to AWS (default)
   agentstr deploy my_agent.py \
       --env OPENAI_API_KEY=$OPENAI_API_KEY \
       --pip openai langchain

   # Change provider per command
   agentstr deploy bot.py --provider gcp --cpu 2 --memory 1024

   # View logs
   agentstr logs bot

   # Destroy
   agentstr destroy bot
