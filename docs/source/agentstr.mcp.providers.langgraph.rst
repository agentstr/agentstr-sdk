LangGraph MCP Provider
=========================

This module provides integration with `LangGraph <https://python.langchain.com/docs/langgraph>`_, allowing conversion between MCP tools and LangGraph's tool format.

Overview
--------

The primary function in this module is ``to_langgraph_tools``, which takes a ``NostrMCPClient`` instance and converts the available MCP tools into a list of tools compatible with LangGraph agents, such as those created with ``langgraph.prebuilt.create_react_agent``.

**Typical usage:**

.. code-block:: python

   import asyncio
   from langgraph.prebuilt import create_react_agent
   from langchain_openai import ChatOpenAI
   from agentstr.mcp.providers.langgraph import to_langgraph_tools
   from agentstr.mcp.nostr_mcp_client import NostrMCPClient

   # Assume nostr_mcp_client is an initialized and connected NostrMCPClient
   async def setup_langgraph_agent(nostr_mcp_client: NostrMCPClient):
       # Convert MCP tools to LangGraph format
       langgraph_tools = await to_langgraph_tools(nostr_mcp_client)

       # Create a LangGraph agent with the converted tools
       agent = create_react_agent(
           model=ChatOpenAI(),
           tools=langgraph_tools
       )
       return agent

Reference
---------

.. automodule:: agentstr.mcp.providers.langgraph
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../agentstr.agents.providers.langgraph` — For using LangGraph agents with Agentstr.
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client used to fetch MCP tools.
