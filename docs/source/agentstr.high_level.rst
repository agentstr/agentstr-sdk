Agentstr Agents
===============

Agentstr provides a high-level interface for creating and deploying sophisticated agents on the Nostr network with minimal setup. It is designed to get you up and running in minutes, handling the boilerplate so you can focus on your agent's logic.

Key Features
------------

Agentstr comes with a rich set of features available out of the box:

*   **Zero-Configuration Deployment**: Launch your agent with just a few lines of code. Agentstr automatically handles the underlying complexities of agent creation and server setup.

*   **State Persistence**: Your agent's conversations and state are automatically persisted. Agentstr supports both SQLite and PostgreSQL for robust data management, with no manual setup required.

*   **Streaming Payments**: Easily monetize your agent. Stratum has built-in support for Nostr Wallet Connect, allowing your agent to request and receive streaming payments (Zaps) for its services.

*   **Human-in-the-Loop**: Seamlessly integrate human oversight and interaction into your agent's workflow. This is crucial for tasks requiring validation, or for creating collaborative human-AI systems.

*   **Extensible through MCPs**: Stratum agents can be extended with new skills and tools via the Model Control Protocol (MCP). This allows you to connect to other agents or services on the Nostr network, creating powerful, decentralized applications.

Getting Started
---------------

Here's a quick example of how to launch an Agentstr agent:

.. code-block:: python

   import asyncio
   import os
   from agentstr import AgentstrAgent, NostrClient

   # Set up your environment variables
   os.environ["LLM_BASE_URL"] = "your-llm-api-base-url"
   os.environ["LLM_API_KEY"] = "your-llm-api-key"
   os.environ["LLM_MODEL_NAME"] = "your-llm-model"
   PRIVATE_KEY_NSEC = "your-nostr-private-key"

   async def main():
       # Initialize the Nostr client
       nostr_client = NostrClient(private_key_nsec=PRIVATE_KEY_NSEC)
       
       # Create and start the Agentstr agent
       agent = AgentstrAgent(
           nostr_client=nostr_client,
           name="My Awesome Agent",
           description="An agent that can do amazing things."
       )
       await agent.start()

   if __name__ == "__main__":
       asyncio.run(main())


For a detailed API reference, see the :doc:`agentstr.agents.agentstr` page.
