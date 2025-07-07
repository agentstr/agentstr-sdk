Model Context Protocol (MCP)
============================

The Model Context Protocol (MCP) is a key feature of the Agentstr SDK, enabling seamless integration with various AI models and services. MCP allows your agents to leverage external capabilities, enhancing their functionality. Refer to :doc:`../../agentstr.mcp` for an overview of MCP.

Key MCP components include:

- **Nostr MCP Client**: Refer to :doc:`../../agentstr.mcp.nostr_mcp_client` for details on the client-side implementation.
- **Nostr MCP Server**: Refer to :doc:`../../agentstr.mcp.nostr_mcp_server` for details on the server-side implementation.

MCP Providers
-------------

Nostr MCP Servers adhere to the Model Context Protocol (MCP), providing a standardized way to offer tools and services. However, different agentic frameworks may integrate with MCP in slightly different ways due to their unique architectures and requirements. MCP Providers in Agentstr SDK bridge this gap, ensuring that Nostr MCP Servers can be seamlessly used by any agentic framework. Here are the available MCP providers:

Available MCP Providers
~~~~~~~~~~~~~~~~~~~~~~~

*   :doc:`../../agentstr.mcp.providers.agno`
*   :doc:`../../agentstr.mcp.providers.dspy`
*   :doc:`../../agentstr.mcp.providers.google`
*   :doc:`../../agentstr.mcp.providers.langgraph`
*   :doc:`../../agentstr.mcp.providers.openai`
*   :doc:`../../agentstr.mcp.providers.pydantic`

Check out the :doc:`../../getting_started/creating_an_mcp_server` for a getting started guide on how to create an MCP server.

Relevant Modules
----------------

*   :doc:`../../agentstr.mcp`
*   :doc:`../../agentstr.mcp.nostr_mcp_client`
*   :doc:`../../agentstr.mcp.nostr_mcp_server`
*   :doc:`../../agentstr.mcp.providers`
