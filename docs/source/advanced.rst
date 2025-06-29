Advanced Topics
===============

While :doc:`agentstr` provides a powerful, zero-configuration entry point, `agentstr` also offers a granular, component-based architecture for developers who need more control. This guide explores how to move beyond the `AgentstrAgent` abstraction to build highly customized agents.

Core Components
----------------

At the heart of `agentstr` are two core components:

*   :class:`~agentstr.agents.nostr_agent.NostrAgent`: This class adapts your agent's logic to the Nostr protocol. It takes a `chat_generator`—an async function that processes chat inputs—and handles the communication layer.
*   :class:`~agentstr.agents.nostr_agent_server.NostrAgentServer`: This class wraps a `NostrAgent` and runs it as a persistent server, listening for and responding to events on the Nostr network.

By working with these components directly, you can customize every aspect of your agent's behavior.

Agent Providers
---------------

`agentstr` supports various popular agent frameworks through a flexible provider model. This allows you to bring your own agent logic, written in your preferred framework, and seamlessly connect it to Nostr.

Here are the supported providers:

*   **LangGraph**: See :doc:`agentstr.agents.providers.langgraph`.

*   **DSPy**: See :doc:`agentstr.agents.providers.dspy`.

*   **OpenAI**: See :doc:`agentstr.agents.providers.openai`.

*   **Google**: See :doc:`agentstr.agents.providers.google`.

*   **Agno**: See :doc:`agentstr.agents.providers.agno`.

*   **Pydantic**: See :doc:`agentstr.agents.providers.pydantic`.

Extending with MCPs
-------------------

The `Model Context Protocol (MCP) <agentstr.mcp>` allows agents to discover and use tools and skills from other agents on the Nostr network. The :class:`~agentstr.mcp.nostr_mcp_client.NostrMCPClient` is used to interact with MCP servers, dynamically extending your agent's capabilities.

Cookbook Examples
-----------------

The `cookbook/` directory contains practical, real-world examples that demonstrate how to use these advanced features.

**Agent Examples (`cookbook/agents/`)**

*   **Finance**: An agent that can fetch stock prices. See the `finance example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/finance>`_.
*   **Travel**: An agent that can help plan trips. See the `travel example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/travel>`_.
*   **Nostr RAG**: An agent that performs RAG over Nostr notes. See the `Nostr RAG example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/nostr_rag>`_.

**MCP Server Examples (`cookbook/mcp_servers/`)**

*   **Web Search**: An MCP server that provides web search capabilities. See the `web search example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/mcp_servers/web_search>`_.
*   **Bitcoin**: An MCP server for fetching Bitcoin data. See the `Bitcoin example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/mcp_servers/bitcoin>`_.

By studying these examples, you can learn how to combine different providers and MCPs to build sophisticated, decentralized applications.
