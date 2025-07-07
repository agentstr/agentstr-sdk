Nostr Agent Server
==================

The ``NostrAgentServer`` class provides a high-level interface for running a Nostr agent as a networked server. It manages the connection to the Nostr network, listens for incoming direct messages, and delegates them to the agent for processing.

Usage
-----

.. code-block:: python

   import asyncio
   from agentstr import NostrAgent, NostrAgentServer

   # Initialize the Nostr agent
   nostr_agent = NostrAgent(...)

   # Create and run the server
   async def main():
       server = NostrAgentServer(nostr_agent=nostr_agent)
       await server.start()

   if __name__ == "__main__":
       asyncio.run(main())

.. note::
   See :doc:`nostr_agent` for information on how to create an agent.

Reference
---------

.. automodule:: agentstr.agents.nostr_agent_server
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr` — for a high-level interface to run an agent on Nostr.
- :doc:`nostr_agent` — for adapting an agent to the Nostr protocol.
- :doc:`../agents` — for an overview of all agentic components in the Agentstr SDK.
