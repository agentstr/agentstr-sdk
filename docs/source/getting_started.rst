Getting Started
===============

Welcome to Agentstr SDK! This short guide helps you spin up quickly after installation.

1. Create a Python virtual environment and install the SDK (see :doc:`installation`).
2. Initialise a new agent project:

   .. code-block:: bash

      agentstr init my_agent

3. Start the development relay:

   .. code-block:: bash

      agentstr relay run

4. Run your agent locally:

   .. code-block:: bash

      python my_agent/main.py

5. Test your agent locally:

   .. code-block:: bash

      python my_agent/test_client.py

Next Steps
----------

* Browse the :doc:`Core Modules <agentstr>` for in-depth API details.
* Check out the `Examples <https://github.com/agentstr/agentstr-sdk/tree/main/examples>`_ directory for more in-depth examples.
* Deploy your agent to the cloud with :doc:`Cloud CI/CD <cloud_cicd>`.
