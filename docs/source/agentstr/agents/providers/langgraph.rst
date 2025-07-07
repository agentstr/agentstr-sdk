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

    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    from agentstr import NostrAgentServer, NostrMCPClient, NostrAgent, AgentCard
    from agentstr.mcp.providers.langgraph import to_langgraph_tools
    from agentstr.agents.providers.langgraph import langgraph_chat_generator

    # Note: To run this example, you need the Agentstr LangGraph extra
    # pip install agentstr-sdk[langgraph]

    # 1. Create react agent
    my_langgraph_agent = create_react_agent(
        model=ChatOpenAI(),
        prompt="You are a helpful assistant",
    )

    # 2. Create LangGraph chat generator
    chat_generator = langgraph_chat_generator(my_langgraph_agent, [nostr_mcp_client])

    # 3. Create Nostr Agent
    nostr_agent = NostrAgent(
        agent_card=AgentCard(name="LangGraphBot", description="An agent powered by LangGraph."),
        chat_generator=chat_generator)

    # This `nostr_agent` can now be used with a NostrAgentServer to expose
    # the LangGraph agent over the Nostr protocol.


Reference
---------

.. automodule:: agentstr.agents.providers.langgraph
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../mcp/providers/langgraph` — for LangGraph MCP integration.
- `LangGraph Example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/langgraph_agent.py>`_ - A complete example of using LangGraph with Agentstr.