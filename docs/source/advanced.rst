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

Scheduling
----------

`agentstr` includes a built-in scheduler for running asynchronous jobs at specified intervals or times. The :class:`~agentstr.scheduler.Scheduler` class wraps the `APScheduler` library, providing a simple interface for scheduling tasks within your agent.

Here’s how you can use it:

.. code-block:: python

    from agentstr.scheduler import Scheduler

    async def my_periodic_task():
        print("This task runs every 10 seconds.")

    scheduler = Scheduler()
    scheduler.add_job(my_periodic_task, "interval", seconds=10)
    scheduler.start()

Persistence
-----------

`agentstr` supports persistence for storing user data and message history. This is handled by the :class:`~agentstr.database.database.Database` class, which provides an abstraction over different database backends.

**Supported Backends:**

*   **SQLite**: The default, file-based database.
*   **Postgres**: For production environments, via `asyncpg`.

**Message History**

The :class:`~agentstr.database.message_history.MessageHistory` class provides an interface for storing and retrieving conversation histories, which is essential for context-aware agents.

Commands
--------

Agents can be equipped with a command handling system that allows them to respond to specific, exclamation-prefixed messages (e.g., `!help`). The :class:`~agentstr.commands.DefaultCommands` class routes these commands to registered asynchronous handler functions.

**Default Commands:**

*   `!help`: Lists available commands.
*   `!describe`: Provides a description of the agent.
*   `!balance`: Shows the user's current balance.
*   `!deposit <amount>`: Provides a deposit address for the user to top up their balance.

Model Context Protocol (MCP)
----------------------------

The `Model Context Protocol (MCP) <agentstr.mcp>` allows agents to discover and use tools and skills from other agents on the Nostr network. This enables a decentralized ecosystem of specialized agents that can collaborate to perform complex tasks.

The :class:`~agentstr.mcp.nostr_mcp_client.NostrMCPClient` is used to interact with MCP servers, dynamically extending your agent's capabilities. The :class:`~agentstr.mcp.nostr_mcp_server.NostrMCPServer` allows you to expose your agent's tools to the network.

Payments
--------

`agentstr` has built-in support for handling payments via the Nostr Wallet Connect (NWC) protocol. The :class:`~agentstr.relays.nwc_relay.NWCRelay` class provides an interface for sending and receiving payments.

This is integrated with the MCP server to allow for paid tools, where an agent can charge for the use of its services.

Cookbook Examples
-----------------

The `cookbook/` directory contains practical, real-world examples that demonstrate how to use these advanced features.

**Agent Examples (`cookbook/agents/`)**

*   **Finance**: An agent that can fetch stock prices. See the `Finance example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/finance>`_.
*   **Travel**: An agent that can help plan trips. See the `Travel example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/travel>`_.
*   **Nostr RAG**: An agent that performs RAG over Nostr notes. See the `Nostr RAG example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/nostr_rag>`_.

**MCP Server Examples (`cookbook/mcp_servers/`)**

*   **Web Search**: An MCP server that provides web search capabilities. See the `Web Search example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/mcp_servers/web_search>`_.
*   **Bitcoin**: An MCP server for fetching Bitcoin data. See the `Bitcoin example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/mcp_servers/bitcoin>`_.

By studying these examples, you can learn how to combine different providers and MCPs to build sophisticated, decentralized applications.
