Tool Calling Agent
=====================

This guide will walk you through creating an agent that can call external tools using the Agentstr SDK, expanding on the concepts from the 'Simple Agent' example.

Step 1: Initialize Your Project
-------------------------------

Start by initializing a new project if you haven't already:

.. code-block:: bash

   agentstr init tool_agent

This sets up a `tool_agent` directory with the necessary structure.

Step 2: Define Tools for Your Agent
-----------------------------------

Open `tool_agent/main.py` and modify it to include tool calling functionality. You'll need to integrate with the Model Context Protocol (MCP) for tool access.

.. code-block:: python

   import asyncio
   from agentstr import NostrAgent, AgentCard, ChatInput, ChatOutput
   from agentstr.mcp.nostr_mcp_client import NostrMCPClient

   async def tool_enabled_chat(input: ChatInput):
       mcp_client = NostrMCPClient(server_public_key="<your-mcp-server-key>")
       await mcp_client.connect()
       tools = await mcp_client.list_tools()
       # Example: Use a tool if available
       if tools:
           yield ChatOutput(message=f"I can use tools! Available tools: {tools}")
       else:
           yield ChatOutput(message="No tools available at the moment.")
       await mcp_client.disconnect()

   agent_card = AgentCard(name="ToolAgent", description="An agent with tool calling capabilities")
   nostr_agent = NostrAgent(agent_card=agent_card, chat_generator=tool_enabled_chat)

   # Continue with the standard setup for running the agent

.. note::
   Replace `<your-mcp-server-key>` with the actual public key of an MCP server you have access to. If you're testing locally, ensure an MCP server is set up as described in the :doc:`../../agentstr.mcp.nostr_mcp_server` documentation.

Step 3: Start a Local Relay
---------------------------

Start a local Nostr relay for testing:

.. code-block:: bash

   agentstr relay start

Keep this running in a separate terminal.

Step 4: Run Your Tool-Enabled Agent
-----------------------------------

Run your agent with tool calling capabilities:

.. code-block:: bash

   python tool_agent/main.py

Step 5: Test Your Agent
-----------------------

Use the test client to interact with your agent and see the tool listing response:

.. code-block:: bash

   python tool_agent/test_client.py

You should see a response indicating available tools or a message if none are available.

.. note::
   If you encounter connection issues with the MCP server, ensure the server is running and accessible. Refer to troubleshooting tips in the :doc:`hello_world` guide for general connectivity issues.


Step 6: Cloud Deployment
------------------------

Deploy your Tool Calling Agent to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f tool_agent/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

Next Steps
----------

- **Expand Tool Integration**: Explore more MCP tools and services to enhance your agent's capabilities. Check out :doc:`../key_concepts/mcp` for advanced integration techniques.
- **Enhance Agent Logic**: Customize how your agent decides which tools to call based on user input or context.
- **Explore More Examples**: Check out the :doc:`payment_enabled_agent` guide for adding payment processing to your agent.