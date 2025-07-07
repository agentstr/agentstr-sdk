Agentstr Agent
==============

The ``AgentstrAgent`` is a high-level class for streamlining agent creation on Nostr. It simplifies agent deployment with out-of-the-box support for state persistence, streaming payments, and human-in-the-loop capabilities, all with zero configuration required.

See :doc:`getting_started/simple_agent` for a basic example.

Overview
--------

**Typical usage:**

.. code-block:: python

   import asyncio
   import os
   from agentstr import AgentstrAgent

   # Required environment variables for the LLM
   os.environ["LLM_BASE_URL"] = "https://api.openai.com/v1"
   os.environ["LLM_API_KEY"] = "your-api-key"
   os.environ["LLM_MODEL_NAME"] = "gpt-4"

   # A private key for the agent's Nostr identity
   os.environ["NOSTR_NSEC"] = "your-nostr-private-key"

   async def main():
       # Create and start the Agentstr agent
       agentstr_agent = AgentstrAgent(
           name="MyAgentstrAgent",
           description="A helpful assistant powered by Agentstr."
       )
       await agentstr_agent.start()

   if __name__ == "__main__":
       # Run the agent
       asyncio.run(main())

.. note::
   You should set these environment variables in a .env file or some other secure mechanism.

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
