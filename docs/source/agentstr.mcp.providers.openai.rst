OpenAI MCP Integration
======================

This module provides integration with `OpenAI's <https://openai.com/>`_ tools, enabling conversion between MCP tools and OpenAI's tool format.

Overview
--------

The primary function in this module is ``to_openai_tools``, which takes a ``NostrMCPClient`` instance and converts the available MCP tools into a format that can be used by an OpenAI-compatible agent.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel
   from agentstr.mcp.providers.openai import to_openai_tools
   from agentstr.mcp.nostr_mcp_client import NostrMCPClient

   # Assume nostr_mcp_client is an initialized and connected NostrMCPClient
   async def setup_openai_agent(nostr_mcp_client: NostrMCPClient):
       # Convert MCP tools to OpenAI format
       openai_tools = await to_openai_tools(nostr_mcp_client)

       # Create an OpenAI agent with the converted tools
       agent = Agent(
           model=OpenAIChatCompletionsModel(
               model="gpt-4-turbo",
               openai_client=AsyncOpenAI()
           ),
           tools=openai_tools,
       )
       return agent

Reference
---------

.. automodule:: agentstr.mcp.providers.openai
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.agents.providers.openai` — For using OpenAI agents with Agentstr.
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client used to fetch MCP tools.
