NostrAgent
==========

The ``NostrAgent`` class adapts an agent (such as an LLM or callable) to the Nostr chat protocol. It supports both streaming and non-streaming interfaces, and exposes a unified async chat API for use in Nostr-compatible applications.

Overview
--------

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr import NostrAgent, AgentCard, ChatInput, ChatOutput

   # Define a simple agent callable
   async def simple_chat(input: ChatInput):
       yield ChatOutput(message=f"Echo: {input.message}")

   agent_card = AgentCard(name="EchoBot", description="Echoes your input")
   nostr_agent = NostrAgent(agent_card=agent_card, chat_generator=simple_chat)

   # Streaming chat usage
   async def main():
       async for chunk in nostr_agent.chat_stream(ChatInput(message="Hello!", thread_id="t1", user_id="u1")):
           print(chunk.message)

   asyncio.run(main())

Reference
---------

.. automodule:: agentstr.agents.nostr_agent
   :members:
   :undoc-members:
   :show-inheritance:


See Also
--------
- :class:`agentstr.agents.nostr_agent_server.NostrAgentServer` — for exposing a NostrAgent as a networked server.
- :doc:`agentstr.agents` — for an overview of all agent adapters.

