PydanticAI MCP Provider
=======================

This module provides integration with `PydanticAI <https://ai.pydantic.dev/>`_, enabling conversion between MCP tools and PydanticAI's tool format.

Overview
--------

The primary function in this module is ``to_pydantic_tools``, which takes a ``NostrMCPClient`` instance and converts the available MCP tools into a list of Pydantic models that can be used by a ``pydantic_ai.Agent``.

Usage
~~~~~

.. code-block:: python

   from pydantic_ai import Agent
   from pydantic_ai.models.openai import OpenAIModel
   from agentstr import NostrMCPClient
   from agentstr.mcp.providers.pydantic import to_pydantic_tools

   # Assume nostr_mcp_client is an initialized and connected NostrMCPClient
   async def setup_pydantic_agent(nostr_mcp_client: NostrMCPClient):
       # Convert MCP tools to PydanticAI format
       pydantic_tools = await to_pydantic_tools(nostr_mcp_client)

       # Create a PydanticAI agent with the converted tools
       agent = Agent(
           system="You are a helpful assistant.",
           model=OpenAIModel("gpt-4-turbo"),
           tools=pydantic_tools,
       )
       return agent

.. note::
   For a complete, working example, check out the `PydanticAI Agent example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/pydantic_agent.py>`_.

Reference
---------

.. automodule:: agentstr.mcp.providers.pydantic
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../agents/providers/pydantic` — For using PydanticAI agents with Agentstr.
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client used to fetch MCP tools.
