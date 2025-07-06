Creating an MCP Server
=======================

This guide explains how to create and run a Model Context Protocol (MCP) server using the Agentstr SDK. MCP servers provide tools that agents can call.

Step 1: Set Up Your Environment
--------------------------------

If you haven't already, initialize a new project:

.. code-block:: bash

   agentstr init mcp_server

Step 2: Define Your Tools
-------------------------

Modify `mcp_server/main.py` to define the tools you want to expose as tools.

.. code-block:: python

    from agentstr import NostrMCPServer, tool

    # Addition tool
    async def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    # Multiplication tool
    async def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    # Weather tool
    async def get_weather(city: str) -> str:
        """Get weather for a given city."""
        return f"It's always sunny in {city}!"


Step 3: Create and Run the Server
---------------------------------

In the same file, create an instance of `NostrMCPServer` and start it.

.. code-block:: python

    import os
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()

    relays = os.getenv("NOSTR_RELAYS").split(",")
    private_key = os.getenv("MCP_SERVER_NSEC")
    nwc_str = os.getenv("MCP_SERVER_NWC_CONN_STR")

    async def run():
        # Define the server
        server = NostrMCPServer(
            "Math MCP Server",
            relays=relays,
            private_key=private_key,
            nwc_str=nwc_str,
            tools=[add, multiply, get_weather],
        )

        # Start the server
        await server.start()

    if __name__ == "__main__":
        asyncio.run(run())


Step 4: Run the MCP Server
--------------------------

Execute the script from your terminal:

.. code-block:: bash

   python mcp_server.py

Your MCP server is now running and ready to provide tools to your agents.

Next Steps
----------

- **Create an Agent that Uses Tools**: See the :doc:`tool_calling_agent` guide to learn how to create an agent that can connect to this MCP server and use its tools.
