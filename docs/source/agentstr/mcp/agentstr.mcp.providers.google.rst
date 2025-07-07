Google MCP Provider
======================

This module provides integration with Google's agent development tools, allowing for the use of MCP-defined tools within Google's ecosystem (e.g., with Gemini).

Overview
--------

The primary function in this module is ``to_google_tools``, which takes a ``NostrMCPClient`` instance and converts the available MCP tools into a format that can be used by a ``google.adk.agents.Agent``.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.mcp.providers.google import to_google_tools
   from agentstr.mcp.nostr_mcp_client import NostrMCPClient
   from google.adk.agents import Agent
   from google.adk.models.lite_llm import LiteLlm

   # Assume nostr_mcp_client is an initialized and connected NostrMCPClient
   async def setup_google_agent(nostr_mcp_client: NostrMCPClient):
       # Convert MCP tools to Google format
       google_tools = await to_google_tools(nostr_mcp_client)

       # Create a Google agent with the converted tools
       agent = Agent(
           model=LiteLlm(),
           tools=google_tools,
       )
       return agent

Reference
---------

.. automodule:: agentstr.mcp.providers.google
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.agents.providers.google` — For using Google agents with Agentstr.
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client used to fetch MCP tools.
