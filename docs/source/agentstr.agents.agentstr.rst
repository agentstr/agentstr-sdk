Stratum
=======

The ``StratumAgent`` is a high-level class for streamlining agent creation on Nostr. It simplifies agent deployment with out-of-the-box support for state persistence, streaming payments, and human-in-the-loop capabilities, all with zero configuration required.

Overview
--------

**Typical usage:**

.. code-block:: python

   import asyncio
   import os
   from agentstr import AgentstrAgent, NostrClient

   # Required environment variables for the LLM
   os.environ["LLM_BASE_URL"] = "https://api.openai.com/v1"
   os.environ["LLM_API_KEY"] = "your-api-key"
   os.environ["LLM_MODEL_NAME"] = "gpt-4"

   # A private key for the agent's Nostr identity
   PRIVATE_KEY_NSEC = "your-nostr-private-key"

   async def main():
       # Initialize the Nostr client
       nostr_client = NostrClient(private_key_nsec=PRIVATE_KEY_NSEC)
       
       # Create and start the Agentstr agent
       agentstr_agent = AgentstrAgent(
           nostr_client=nostr_client,
           name="MyAgentstrAgent",
           description="A helpful assistant powered by Agentstr."
       )
       await agentstr_agent.start()

   if __name__ == "__main__":
       # To run this, you would typically use asyncio.run(main())
       # In a real application, this would keep running to listen for events.
       pass

Reference
---------

.. automodule:: agentstr.agents.agentstr
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`~agentstr.agents.nostr_agent.NostrAgent` — The underlying agent class.
- :class:`~agentstr.agents.nostr_agent_server.NostrAgentServer` — The server that hosts the agent.
- :doc:`agentstr.agents` — for an overview of all agent adapters.
