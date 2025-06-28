Command-Line Interface
======================

The ``agentstr.cli`` module provides a command-line interface (CLI) for managing and running Agentstr services. It allows you to start agent servers, manage configurations, and interact with the framework from your terminal.

Overview
--------

The CLI is the primary way to run a Nostr agent server. You can use it to load a configuration file and start the server process.

**Typical usage:**

.. code-block:: bash

   # Display help and see available commands
   agentstr --help

   # Run an agent server using a configuration file
   agentstr run --config /path/to/your/config.yaml

Reference
---------

.. automodule:: agentstr.cli
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`cloud_cicd` — for details on deploying agents using the CLI.
