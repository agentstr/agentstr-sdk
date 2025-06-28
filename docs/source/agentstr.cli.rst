Command-Line Interface
======================

The ``agentstr.cli`` module provides a command-line interface (CLI) for managing and running Agentstr services, primarily for deploying agents to cloud providers.

Overview
--------

The CLI offers commands for the entire lifecycle of an agent deployment, from scaffolding a new project to deploying, monitoring, and destroying it. It supports multiple cloud providers (AWS, GCP, Azure) and manages configurations and secrets.

Commands
--------

- ``agentstr init <project_name>``: Creates a new agent project skeleton.
- ``agentstr deploy <file_path>``: Deploys an application to the configured cloud provider.
- ``agentstr list``: Lists active deployments.
- ``agentstr logs <name>``: Fetches logs for a specific deployment.
- ``agentstr destroy <name>``: Removes a deployment and its resources.
- ``agentstr put-secret <key> <value>``: Stores a single secret in the provider's secret manager.
- ``agentstr put-secrets <env_file>``: Stores multiple secrets from a ``.env`` file.
- ``agentstr relay run``: Runs a local Nostr relay for development purposes.

**Typical usage:**

.. code-block:: bash

   # Get help on all commands
   agentstr --help

   # Create a new agent project
   agentstr init my-new-agent

   # Deploy an agent to the cloud
   agentstr deploy my-new-agent/main.py --provider aws --name my-first-agent

Reference
---------

.. automodule:: agentstr.cli
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`cloud_cicd` — for details on deploying agents using the CLI.
