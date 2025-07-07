Agentstr Agent
==============

The ``AgentstrAgent`` is a high-level class for streamlining agent creation on Nostr. It simplifies agent deployment with out-of-the-box support for state persistence, streaming payments, and human-in-the-loop capabilities, all with minimal configuration required.

See the :doc:`../../getting_started/simple_agent` for a basic example.

See the :doc:`../../getting_started/tool_calling_agent` for a more advanced example.

Usage
-----

.. code-block:: python

   import asyncio
   from agentstr import AgentstrAgent

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
   Check out the :doc:`../../getting_started/simple_agent` for a configuring the required environment variables.

Reference
---------

.. automodule:: agentstr.agents.agentstr
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`~agentstr.agents.agentstr.AgentstrAgent` — The high-level agent class.
- :class:`~agentstr.agents.nostr_agent.NostrAgent` — The underlying agent class.
- :class:`~agentstr.agents.nostr_agent_server.NostrAgentServer` — The server that hosts the agent.
- :doc:`../agents` — for an overview of all agent functionality within the Agentstr SDK.