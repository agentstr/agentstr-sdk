Agentstr CLI
============

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
- ``agentstr relay start``: Runs a local Nostr relay for development purposes.

**Typical usage:**

.. code-block:: bash

   # Get help on all commands
   agentstr --help

   # Create a new agent project
   agentstr init my-new-agent

   # Deploy the agent to the cloud
   agentstr deploy -f my-new-agent/config.yaml

Reference
---------

.. click:: agentstr.cli:init_cmd
   :prog: agentstr init
   :nested: full

.. click:: agentstr.cli:deploy
   :prog: agentstr deploy
   :nested: full

.. click:: agentstr.cli:list_cmd
   :prog: agentstr list
   :nested: full

.. click:: agentstr.cli:logs
   :prog: agentstr logs
   :nested: full

.. click:: agentstr.cli:destroy
   :prog: agentstr destroy
   :nested: full

.. click:: agentstr.cli:relay
   :prog: agentstr relay
   :nested: full


See Also
--------
- :doc:`../cloud_cicd` — for details on deploying agents using the CLI.
