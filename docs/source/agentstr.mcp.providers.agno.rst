Agno Integration
================

This module provides integration with `Agno <https://github.com/agnoauth/agno>`_ tools, allowing conversion between MCP tools and Agno's function format.

Overview
--------

The primary function in this module is ``to_agno_tools``, which takes a ``NostrMCPClient`` instance and converts the available MCP tools into a format that can be used by an ``agno.agent.Agent``.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.mcp.providers.agno import to_agno_tools
   from agentstr.mcp.nostr_mcp_client import NostrMCPClient
   from agno.agent import Agent
   from agno.models.openai import OpenAIChat

   # Assume nostr_mcp_client is an initialized and connected NostrMCPClient
   async def setup_agno_agent(nostr_mcp_client: NostrMCPClient):
       # Convert MCP tools to Agno format
       agno_tools = await to_agno_tools(nostr_mcp_client)

       # Create an Agno agent with the converted tools
       agent = Agent(
           model=OpenAIChat(),
           tools=agno_tools,
       )
       return agent

Reference
---------

.. automodule:: agentstr.mcp.providers.agno
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.agents.providers.agno` — For using Agno agents with Agentstr.
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client used to fetch MCP tools.

