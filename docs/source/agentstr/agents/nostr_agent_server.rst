Nostr Agent Server
==================

The ``NostrAgentServer`` class provides a high-level interface for running a Nostr agent as a networked server. It manages the connection to the Nostr network, listens for incoming events, and delegates them to the appropriate agent for processing.

Overview
--------

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr import NostrAgent, NostrAgentServer, AgentCard, ChatInput, ChatOutput

   # Define a simple agent
   async def simple_chat(input: ChatInput):
       yield ChatOutput(message=f"Echo: {input.message}")

   agent_card = AgentCard(name="EchoBot", description="Echoes your input")
   nostr_agent = NostrAgent(agent_card=agent_card, chat_generator=simple_chat)

   # Create and run the server
   server = NostrAgentServer(nostr_agent=nostr_agent)

   async def main():
       await server.start()

   if __name__ == "__main__":
       asyncio.run(main())

Reference
---------

.. automodule:: agentstr.agents.nostr_agent_server
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.agents.nostr_agent.NostrAgent` — for adapting an agent to the Nostr protocol.
- :doc:`agentstr.agents` — for an overview of all agent adapters.
