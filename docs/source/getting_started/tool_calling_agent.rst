Tool Calling Agent
=====================

This guide will walk you through creating an agent that can call external tools using the Agentstr SDK, expanding on the concepts from the :doc:`payment_enabled_agent` example.

Step 1: Initialize Your Project
-------------------------------

Start by initializing a new project if you haven't already:

.. code-block:: bash

   agentstr init tool_calling_agent

This sets up a `tool_calling_agent` directory with the necessary structure.

Step 2: Update .env file
------------------------

Update the `tool_calling_agent/.env` file with your LLM information and NWC connection string.

.. code-block:: bash

   LLM_BASE_URL=https://api.openai.com/v1
   LLM_API_KEY=your-api-key
   LLM_MODEL_NAME=gpt-3.5-turbo
   NWC_CONN_STR=nostr+walletconnect://<your-nwc-connection-string>
   MCP_SERVER_PUBKEY=<your-mcp-server-public-key>

.. note::
   - `NWC_CONN_STR` is the default environment variable for `NWCRelay` to enable Nostr Wallet Connect. You can override this by passing a connection string directly to the `NostrClient` constructor.
   - `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL_NAME` are the default environment variables for `AgentstrAgent` to enable LLM integration. You can override these by passing a connection string directly to the `AgentstrAgent` constructor.
   - Replace `<your-mcp-server-key>` with the actual public key of a Nostr MCP server you have access to. If you're testing locally, ensure an MCP server is set up as described in the :doc:`../../agentstr.mcp.nostr_mcp_server` documentation.
   - You can follow the :doc:`creating_an_mcp_server` guide to set up Nostr MCP server.
   
Step 3: Define Tools for Your Agent
-----------------------------------

Open `tool_calling_agent/main.py` and modify it to include tool calling functionality. You'll need to integrate with the Model Context Protocol (MCP) for tool access.

.. literalinclude:: ../../../getting_started/tool_calling_agent/main.py
   :language: python
   :linenos:

Step 4: Update Test Client
--------------------------

Update `tool_calling_agent/test_client.py` to interact with your tool-enabled agent.

.. literalinclude:: ../../../getting_started/tool_calling_agent/test_client.py
   :language: python
   :linenos:

Step 5: Start a Local Relay
---------------------------

Start a local Nostr relay for testing:

.. code-block:: bash

   agentstr relay start

Keep this running in a separate terminal.

Step 6: Run Your Tool-Enabled Agent
-----------------------------------

Run your agent with tool calling capabilities:

.. code-block:: bash

   python tool_calling_agent/main.py

Step 7: Test Your Agent
-----------------------

Use the test client to interact with your agent and see the tool listing response:

.. code-block:: bash

   python tool_calling_agent/test_client.py

You should see a response indicating available tools or a message if none are available.

.. note::
   If you encounter connection issues with the MCP server, ensure the server is running and accessible. Refer to troubleshooting tips in the :doc:`hello_world` guide for general connectivity issues.


Step 7: Cloud Deployment
------------------------

Deploy your Tool Calling Agent to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f tool_calling_agent/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

Next Steps
----------

- **Expand Tool Integration**: Explore more MCP tools and services to enhance your agent's capabilities. Check out :doc:`../key_concepts/mcp` for advanced integration techniques.
