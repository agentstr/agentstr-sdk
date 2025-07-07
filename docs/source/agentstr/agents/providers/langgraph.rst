LangGraph Provider
==================

The ``agentstr.agents.providers.langgraph`` module provides integration between Agentstr and the `LangGraph <https://www.langchain.com/langgraph>`_ agent framework. It enables you to use LangGraph graphs as chat agents within the Agentstr SDK, supporting streaming, tool calls, and payment-aware responses.

Overview
--------

The main utility is :func:`langgraph_chat_generator`, which adapts a compiled LangGraph graph into an async chat generator compatible with the Agentstr agent interface. This allows you to:

- Stream agent responses from LangGraph graphs
- Integrate tool call pricing with NostrMCPClient
- Use LangGraph as a backend for NostrAgent or NostrAgentServer

**Example usage:**

.. code-block:: python

   import asyncio
   from typing import TypedDict, Annotated
   from agentstr.agents.providers.langgraph import langgraph_chat_generator
   from agentstr import NostrAgent, AgentCard, ChatInput
   from langgraph.graph import StateGraph
   from langgraph.graph.message import add_messages

   # Note: To run this example, you need LangGraph installed.
   # pip install langgraph

   # 1. Define the state for the LangGraph graph
   class AgentState(TypedDict):
       messages: Annotated[list, add_messages]

   # 2. Define a node for the graph (a simple echo function)
   def echo_node(state: AgentState):
       last_message = state['messages'][-1]
       return {"messages": [("ai", f"Echo: {last_message.content}")]}

   # 3. Create and compile the LangGraph graph
   graph = StateGraph(AgentState)
   graph.add_node("echo", echo_node)
   graph.set_entry_point("echo")
   graph.set_finish_point("echo")
   compiled_graph = graph.compile()

   # 4. Create the chat generator from the compiled graph
   chat_gen = langgraph_chat_generator(compiled_graph)

   # 5. Create the NostrAgent
   agent_card = AgentCard(name="LangGraphEchoBot", description="A simple echo agent.")
   nostr_agent = NostrAgent(agent_card=agent_card, chat_generator=chat_gen)

   # 6. Use the agent in a streaming chat
   async def main():
       async for chunk in nostr_agent.chat_stream(ChatInput(message="Hello!", thread_id="t1", user_id="u1")):
           print(chunk.message)

   if __name__ == "__main__":
       asyncio.run(main())

Reference
---------

.. automodule:: agentstr.agents.providers.langgraph
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../mcp/providers/langgraph` — for LangGraph MCP integration.
