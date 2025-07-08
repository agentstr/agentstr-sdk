Creating an MCP Server
======================

This guide explains how to create and run a Model Context Protocol (MCP) server using the Agentstr SDK. MCP servers provide tools that agents can call.

Step 1: Initialize Your Project
-------------------------------

If you haven't already, initialize a new project:

.. code-block:: bash

   agentstr init mcp_server

This creates a `mcp_server` directory with the basic structure for your MCP server.

Step 2: Update .env File
------------------------

Update the `mcp_server/.env` file with your NWC connection string.

.. code-block:: bash

   NWC_CONN_STR=nostr+walletconnect://<your-nwc-connection-string>

.. note::
   - `NWC_CONN_STR` is the default environment variable for `NWCRelay` to enable Nostr Wallet Connect. You can override this by passing a connection string directly to the `NostrMCPServer` constructor.

Step 3: Define Your Tools
-------------------------

Modify `mcp_server/main.py` to define the tools you want to expose and initialize the MCP Server.

.. literalinclude:: ../../../getting_started/mcp_server/main.py
   :language: python
   :linenos:


Step 4: Modify the Test Client
------------------------------

Modify `mcp_server/test_client.py` to list the tools available and call one of them.

.. literalinclude:: ../../../getting_started/mcp_server/test_client.py
   :language: python
   :linenos:


Step 5: Start a Local Relay
---------------------------

Start a local Nostr relay for testing:

.. code-block:: bash

   agentstr relay start

Keep this running in a separate terminal.

Step 6: Run the MCP Server
--------------------------

Execute the script from your terminal:

.. code-block:: bash

   python mcp_server/main.py

Your MCP server is now running and ready to provide tools to your agents.

Step 7: Test Your MCP Server
----------------------------

Use the test client to interact with your MCP server and check your balance:

.. code-block:: bash

   python mcp_server/test_client.py

You should see a JSON structure defining the available tools, followed by a tool call response.

Step 8 (Optional): Deploy to the Cloud
--------------------------------------

Deploy your MCP Server to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f mcp_server/deploy.yml

   This command packages your MCP server and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

For more information on cloud deployment and CI/CD, see the :doc:`../cloud_cicd` guide.

Next Steps
----------

- **Create an Agent that Uses Tools**: See the :doc:`tool_calling_agent` guide to learn how to create an agent that can connect to this MCP server and use its tools.
- **Explore More MCP Features**: Dive into the :doc:`../key_concepts/mcp` documentation for advanced MCP server configurations and tool creation.
