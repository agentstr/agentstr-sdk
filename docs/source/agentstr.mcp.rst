MCP (Model Context Protocol)
============================

The ``agentstr.mcp`` subpackage implements the Model Context Protocol (MCP) over the Nostr network. It provides the building blocks for creating decentralized tool-using agents that can discover and invoke tools exposed by other entities.

The protocol is divided into two main components:

*   **Client:** The :doc:`agentstr.mcp.nostr_mcp_client` allows an agent to connect to an MCP server, list its available tools, and invoke them.
*   **Server:** The :doc:`agentstr.mcp.nostr_mcp_server` allows an entity to expose a set of tools over Nostr, making them discoverable and invokable by clients.

In addition, the :doc:`agentstr.mcp.providers` submodule offers integrations with popular agent frameworks, making it easy to adapt existing agents to use MCP.

Submodules
----------

.. toctree::
   :maxdepth: 1

   agentstr.mcp.nostr_mcp_client
   agentstr.mcp.nostr_mcp_server

.. toctree::
   :maxdepth: 2

   agentstr.mcp.providers
