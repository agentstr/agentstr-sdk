Nostr MCP Server
================

This module implements a Model Control Protocol (MCP) server that runs over the Nostr network. It allows entities to expose their tools and handle incoming requests from other agents in a decentralized manner using the Nostr protocol.

Overview
--------

The ``NostrMCPServer`` is responsible for exposing a set of tools over Nostr. It listens for requests from ``NostrMCPClient`` instances, executes the requested tool, and returns the result.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.mcp.nostr_mcp_server import NostrMCPServer
   from agentstr.mcp.mcp_server import tool

   # Define a simple tool
   @tool
   def say_hello(name: str) -> str:
       """Says hello to someone."""
       return f"Hello, {name}"

   # Create a server instance and add the tool
   server = NostrMCPServer()
   server.add_tool(say_hello)

   # Run the server
   async def main():
       await server.run()

   if __name__ == "__main__":
       asyncio.run(main())

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
