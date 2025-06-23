Getting Started
===============

Welcome to Agentstr SDK! This short guide helps you spin up quickly after installation.

1. Create a Python virtual environment and install the SDK (see :doc:`installation`).

   .. code-block:: bash

      pip install "agentstr-sdk[cli]"

2. Initialise a new agent project:

   .. code-block:: bash

      agentstr init hello_world

3. Start the development relay:

   .. code-block:: bash

      agentstr relay run

4. Run your agent locally (in a separate terminal):

   .. code-block:: bash

      python hello_world/main.py

5. Test your agent locally (in a separate terminal):

   .. code-block:: bash

      python hello_world/test_client.py

   You should see a response like:

   .. code-block:: bash

      Hello 183ebf080fc59c29ad9c42bff8d6c684955b25611d685df6e03d56779989f149!

Next Steps
----------

* Browse the :doc:`Core Modules <agentstr>` for in-depth API details.
* Check out the `Examples <https://github.com/agentstr/agentstr-sdk/tree/main/examples>`_ directory for more in-depth examples.
* Deploy your agent to the cloud with :doc:`Cloud CI/CD <cloud_cicd>`.
