Nostr MCP Client
================

This module implements a Model Context Protocol (MCP) client over the Nostr network. It enables agents to discover, invoke, and manage tools in a decentralized manner using the Nostr protocol for communication.

Overview
--------

The ``NostrMCPClient`` is responsible for interacting with MCP servers over Nostr. It can be used to list available tools, get tool schemas, and invoke tools with arguments.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.mcp.nostr_mcp_client import NostrMCPClient

   # Assume we have the public key of an MCP server
   server_pubkey = "..."

   # Create a client instance
   client = NostrMCPClient(mcp_server_pubkey=server_pubkey)

   async def main():
       await client.connect()
       # List available tools
       tools = await client.list_tools()
       print(f"Available tools: {tools}")
       # ... invoke tools, etc.
       await client.disconnect()

   asyncio.run(main())

Reference
---------

.. automodule:: agentstr.mcp.nostr_mcp_client
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.mcp.nostr_mcp_server.NostrMCPServer` — The server-side implementation of the MCP protocol.
- :doc:`agentstr.mcp.providers` — For integrations with specific agent frameworks.
