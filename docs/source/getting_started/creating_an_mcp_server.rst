Creating an MCP Server
=======================

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

Step 3: Define Your Tools
-------------------------

Modify `mcp_server/main.py` to define the tools you want to expose and initialize the MCP Server.

.. code-block:: python

    """Simple MCP Server"""

    from dotenv import load_dotenv
    load_dotenv()

    import os
    from agentstr import NostrMCPServer, tool

    # Addition tool
    async def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    # Multiplication tool
    @tool(satoshis=0)
    async def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    # Weather tool (premium tool)
    @tool(satoshis=5)
    async def get_weather(city: str) -> str:
        """Get weather for a given city."""
        return f"It's always sunny in {city}!"


    async def run():
        # Define the server
        server = NostrMCPServer(
            "SimpleMCPServer",
            nwc_str=os.getenv("NWC_CONN_STR"),
            tools=[add, multiply, get_weather],
        )

        # Start the server
        await server.start()


    if __name__ == "__main__":
        import asyncio
        asyncio.run(run())



Step 4: Modify the Test Client
------------------------------

Modify `mcp_server/test_client.py` to list the tools available and call one of them.

.. code-block:: python

    from dotenv import load_dotenv
    load_dotenv()

    import os
    import json
    from agentstr import NostrMCPClient, PrivateKey

    server_public_key = os.getenv("AGENT_PUBKEY")

    async def chat():
        # Initialize the client
        mcp_client = NostrMCPClient(mcp_pubkey=server_public_key,
                                    private_key=PrivateKey().bech32())

        # List available tools
        tools = await mcp_client.list_tools()
        print(f"Found tools: {json.dumps(tools, indent=4)}")

        # Call a tool
        result = await mcp_client.call_tool("add", {"a": 69, "b": 420})
        print(result)


    if __name__ == "__main__":
        import asyncio
        asyncio.run(chat())


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

Step 8: Cloud Deployment
------------------------

Deploy your MCP Server to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f mcp_server/deploy.yml

   This command packages your MCP server and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.


Next Steps
----------

- **Create an Agent that Uses Tools**: See the :doc:`tool_calling_agent` guide to learn how to create an agent that can connect to this MCP server and use its tools.
- **Explore More MCP Features**: Dive into the :doc:`../key_concepts/mcp` documentation for advanced MCP server configurations and tool creation.
