Nostr MCP Server
================

This module implements a Model Control Protocol (MCP) server that runs over the Nostr network. It allows entities to expose their tools and handle incoming requests from other agents in a decentralized manner using the Nostr protocol.

Overview
--------

The ``NostrMCPServer`` is responsible for exposing a set of tools over Nostr. It listens for requests from ``NostrMCPClient`` instances, executes the requested tool, and returns the result, optionally charging the caller via Nostr Wallet Connect (NWC).

Usage
~~~~~

.. code-block:: python

   import asyncio
   from agentstr import NostrMCPServer, tool

   # Define a simple tool
   @tool
   def say_hello(name: str) -> str:
       """Says hello to someone."""
       return f"Hello, {name}"

   # Weather tool (premium tool)
   @tool(satoshis=5)
   async def get_weather(city: str) -> str:
       """Get weather for a given city."""
       return f"It's always sunny in {city}!"

   # Run the server
   async def main():
      # Create a server instance and add the tools
      server = NostrMCPServer(
         "Example MCP Server",
         tools=[say_hello, get_weather],
      )

      # Start the server
      await server.start()

   if __name__ == "__main__":
      asyncio.run(main())

.. note::
   For a complete, working example, check out the `MCP Server example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/mcp_server.py>`_.

Reference
---------

.. automodule:: agentstr.mcp.nostr_mcp_server
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client-side implementation of the MCP protocol.
- :doc:`providers` — For integrations with specific agent frameworks.
