LangGraph MCP Provider
=========================

This module provides integration with `LangGraph <https://www.langchain.com/langgraph>`_, allowing conversion between MCP tools and LangGraph's tool format.

Overview
--------

The primary function in this module is ``to_langgraph_tools``, which takes a ``NostrMCPClient`` instance and converts the available MCP tools into a list of tools compatible with LangGraph agents, such as those created with ``langgraph.prebuilt.create_react_agent``.

Usage
~~~~~

.. code-block:: python

   from langgraph.prebuilt import create_react_agent
   from langchain_openai import ChatOpenAI
   from agentstr import NostrMCPClient
   from agentstr.mcp.providers.langgraph import to_langgraph_tools

   # Assume nostr_mcp_client is an initialized and connected NostrMCPClient
   async def setup_langgraph_agent(nostr_mcp_client: NostrMCPClient):
       # Convert MCP tools to LangGraph format
       langgraph_tools = await to_langgraph_tools(nostr_mcp_client)

       # Create a LangGraph agent with the converted tools
       agent = create_react_agent(
           model=ChatOpenAI(),
           tools=langgraph_tools,
           prompt="You are a helpful assistant",
       )
       return agent

.. note::
   For a complete, working example, check out the `LangGraph Agent example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/langgraph_agent.py>`_.

Reference
---------

.. automodule:: agentstr.mcp.providers.langgraph
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../agents/providers/langgraph` — For using LangGraph agents with Agentstr.
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client used to fetch MCP tools.
