MCP (Model Context Protocol)
============================

The ``agentstr.mcp`` subpackage implements the Model Context Protocol (MCP) over the Nostr network. It provides the building blocks for creating decentralized tool-using agents that can discover and invoke tools exposed by other entities.

The protocol is divided into two main components:

*   **Client:** The :doc:`mcp/nostr_mcp_client` allows an agent to connect to an MCP server, list its available tools, and invoke them.
*   **Server:** The :doc:`mcp/nostr_mcp_server` allows an entity to expose a set of tools over Nostr, making them discoverable and invokable by clients.

In addition, the :doc:`mcp/providers` submodule offers integrations with popular agent frameworks, making it easy to adapt existing agents to use MCP.

Environment Variables
---------------------

`NostrMCPServer` uses the following environment variables by default through its underlying `NostrClient`:

- **NOSTR_RELAYS**: A comma-separated list of relay URLs to connect to. If not provided as a parameter, the client will use this environment variable.
- **NOSTR_NSEC**: The Nostr private key in 'nsec' format for authenticated operations. If not provided as a parameter, the client will look for this environment variable.
- **NWC_CONN_STR**: The Nostr Wallet Connect string for payment processing. If not provided as a parameter, the client will use this environment variable.

.. note::
   You can override these environment variables by passing explicit parameters to the `NostrMCPServer` constructor, such as `relays`, `private_key`, or `nwc_str`.

Submodules
----------

.. toctree::
   :maxdepth: 1

   agentstr.mcp.nostr_mcp_client
   agentstr.mcp.nostr_mcp_server

.. toctree::
   :maxdepth: 2

   agentstr.mcp.providers
