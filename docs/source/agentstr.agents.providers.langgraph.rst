LangGraph Provider
==================

The ``agentstr.agents.providers.langgraph`` module provides integration between Agentstr and the `LangGraph <https://github.com/langchain-ai/langgraph>`_ orchestration framework. It enables you to use LangGraph graphs as chat agents within the Agentstr SDK, supporting streaming, tool calls, and payment-aware responses.

Overview
--------

The main utility is :func:`langgraph_chat_generator`, which adapts a compiled LangGraph graph into an async chat generator compatible with the Agentstr agent interface. This allows you to:

- Stream agent responses from LangGraph graphs
- Integrate tool call pricing with NostrMCPClient
- Use LangGraph as a backend for NostrAgent or NostrAgentServer

**Example usage:**

.. code-block:: python

   from agentstr.agents.providers.langgraph import langgraph_chat_generator
   from agentstr import NostrAgent, AgentCard, ChatInput
   # Assume you have a compiled LangGraph graph and NostrMCPClient
   chat_gen = langgraph_chat_generator(graph, [nostr_mcp_client])
   nostr_agent = NostrAgent(agent_card=AgentCard(name="LangGraphBot", description="LangGraph agent"), chat_generator=chat_gen)

   # Streaming chat
   async for chunk in nostr_agent.chat_stream(ChatInput(message="Hello!", thread_id="t1", user_id="u1")):
       print(chunk.message)

Reference
---------

.. automodule:: agentstr.agents.providers.langgraph
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../agentstr.agents` — for agent adapters overview.
- :doc:`../../agentstr.mcp.providers.langgraph` — for LangGraph MCP integration.
