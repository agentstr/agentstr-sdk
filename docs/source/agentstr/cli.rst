Agentstr CLI
============

The ``agentstr.cli`` module provides a command-line interface (CLI) for managing and running Agentstr services, primarily for deploying agents to cloud providers.

Overview
--------

The CLI offers commands for the entire lifecycle of an agent deployment, from scaffolding a new project to deploying, monitoring, and destroying it. It supports multiple cloud providers (AWS, GCP, Azure, Docker) and manages configurations and secrets.

CLI Commands
~~~~~~~~~~~~

- ``agentstr init <project_name>``: Creates a new agent project skeleton.
- ``agentstr deploy <file_path>``: Deploys an application to the configured cloud provider.
- ``agentstr list``: Lists active deployments.
- ``agentstr logs <name>``: Fetches logs for a specific deployment.
- ``agentstr destroy <name>``: Removes a deployment and its resources.
- ``agentstr relay start``: Runs a local Nostr relay for development purposes.

CLI Usage
~~~~~~~~~

.. code-block:: bash

   # Get help on all commands
   agentstr --help

   # Choose Cloud provider
   export AGENTSTR_PROVIDER=aws # or gcp, azure, docker

   # Create a new agent project
   agentstr init my-new-agent

   # Deploy the agent to the cloud
   agentstr deploy -f my-new-agent/deploy.yml

   # List active deployments
   agentstr list

   # View logs for the deployment
   agentstr logs -f my-new-agent/deploy.yml

   # Destroy the deployment when no longer needed
   agentstr destroy -f my-new-agent/deploy.yml

.. note::
   Make sure your cloud provider credentials are set up before running these commands. See :doc:`../cloud_cicd` for details.

Reference
---------

.. click:: agentstr.cli:cli
   :prog: agentstr
   :nested: full

See Also
--------
- :doc:`../cloud_cicd` — for details on deploying agents using the CLI.
