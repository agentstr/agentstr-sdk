OpenAI MCP Provider
======================

This module provides integration with `OpenAI Agents SDK <https://openai.github.io/openai-agents-python/>`_, enabling conversion between MCP tools and OpenAI's tool format.

Overview
--------

The primary function in this module is ``to_openai_tools``, which takes a ``NostrMCPClient`` instance and converts the available MCP tools into a format that can be used by an OpenAI-compatible agent.

Usage
~~~~~

.. code-block:: python

   from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel
   from agentstr import NostrMCPClient
   from agentstr.mcp.providers.openai import to_openai_tools

   # Assume nostr_mcp_client is an initialized and connected NostrMCPClient
   async def setup_openai_agent(nostr_mcp_client: NostrMCPClient):
       # Convert MCP tools to OpenAI format
       openai_tools = await to_openai_tools(nostr_mcp_client)

       # Create an OpenAI agent with the converted tools
       agent = Agent(
           name="openai_agent",
           instructions="You are a helpful assistant.",
           model=OpenAIChatCompletionsModel(
               model="gpt-4-turbo",
               openai_client=AsyncOpenAI()
           ),
           tools=openai_tools,
       )
       return agent

.. note::
   For a complete, working example, check out the `OpenAI Agent example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/openai_agent.py>`_.

Reference
---------

.. automodule:: agentstr.mcp.providers.openai
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../agents/providers/openai` — For using OpenAI agents with Agentstr.
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client used to fetch MCP tools.
