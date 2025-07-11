Agentstr Agent Framework
========================

The Agentstr SDK simplifies the creation of intelligent agents on the Nostr protocol through its high-level agent class, `AgentstrAgent`. This class offers a ready-to-use framework for building agents with minimal setup, abstracting much of the complexity of agent development. If you're looking to quickly deploy a functional agent without delving into the intricacies of agentic frameworks, `AgentstrAgent` is your starting point.

Key Features
------------

Agentstr comes with a rich set of features available out of the box:

*   **Zero-Configuration Deployment**: Launch your agent with just a few lines of code. Agentstr automatically handles the underlying complexities of Lightning (NWC) and Nostr integration.

*   **State Persistence**: Your agent's conversations and state are automatically persisted. Agentstr supports both SQLite and PostgreSQL for robust data management, with no manual setup required.

*   **Streaming Payments**: Easily monetize your agent. Agentstr has built-in support for Nostr Wallet Connect, allowing your agent to request and receive streaming payments (Zaps) for its services.

*   **Human-in-the-Loop**: Seamlessly integrate human oversight and interaction into your agent's workflow. This is crucial for tasks requiring validation, or for creating collaborative human-AI systems.

*   **Extensible through MCPs**: Agentstr agents can be extended with new skills and tools via the Model Control Protocol (MCP). This allows you to connect to other agents or services on the Nostr network, creating powerful, decentralized applications.

Understanding AgentstrAgent
---------------------------

`AgentstrAgent` is designed as a comprehensive, out-of-the-box solution. It encapsulates core functionalities like message handling, relay connections, and basic agent logic, allowing developers to focus on customizing agent behavior rather than building from scratch. This high-level abstraction is perfect for rapid prototyping or for developers new to the Nostr ecosystem.

For more information on using `AgentstrAgent`, refer to :doc:`../../agentstr/agents/agentstr`.

Using Custom Agentic Frameworks
-------------------------------

While `AgentstrAgent` provides a streamlined approach, the Agentstr SDK also supports advanced customization through agent providers. If you prefer to use a specific agentic framework or need to tailor the agent's logic to your unique requirements, you can select from a variety of agent providers. These providers allow you to integrate frameworks like LangGraph, DSPy, or OpenAI, giving you full control over the agent's underlying architecture. For a detailed exploration of available providers, refer to :doc:`agent_providers`.

Example: Using AgentstrAgent for Quick Setup
--------------------------------------------

Here's a basic example of setting up an agent using `AgentstrAgent`:

.. code-block:: python

   from agentstr.agents.agentstr import AgentstrAgent
   import asyncio

   async def main():
       agent = AgentstrAgent(
           name="MySimpleAgent",
           description="A simple agent for demonstration purposes."
       )
       await agent.start()

   if __name__ == "__main__":
       asyncio.run(main())

This snippet demonstrates how `AgentstrAgent` can be instantiated and started with minimal code, leveraging its built-in capabilities for immediate functionality.

Relevant Modules
----------------

*   :doc:`../../agentstr/agents/agentstr`
