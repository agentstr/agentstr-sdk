Nostr MCP Client
================

This module implements a Model Context Protocol (MCP) client over the Nostr network. It enables agents to discover, invoke, and manage tools in a decentralized manner using the Nostr protocol for communication.

Overview
--------

The ``NostrMCPClient`` is responsible for interacting with MCP servers over Nostr. It can be used to list available tools, get tool schemas, and invoke tools with arguments.

Usage
~~~~~

.. code-block:: python

   import asyncio
   import json
   from agentstr import NostrMCPClient

   # Assume we have the public key of an MCP server
   server_pubkey = "..."

   async def main():
      # Create a client instance
      client = NostrMCPClient(mcp_pubkey=server_pubkey)

      # List available tools
      tools = await client.list_tools()
      print(f"Found tools: {json.dumps(tools, indent=4)}")

      # Call a tool
      result = await client.call_tool("add", {"a": 69, "b": 420})
      print(f'The result of 69 + 420 is: {result["content"][-1]["text"]}')


   if __name__ == "__main__":
      asyncio.run(main())

.. note::
   For a complete, working example, check out the `MCP Client example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/mcp_client.py>`_.


Reference
---------

.. automodule:: agentstr.mcp.nostr_mcp_client
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.mcp.nostr_mcp_server.NostrMCPServer` — The server-side implementation of the MCP protocol.
- :doc:`providers` — For integrations with specific agent frameworks.
