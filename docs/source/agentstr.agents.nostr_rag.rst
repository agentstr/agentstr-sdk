Nostr RAG (Retrieval-Augmented Generation)
==========================================

This module provides classes for building Retrieval-Augmented Generation (RAG) agents that can store and retrieve information from the Nostr network.

Overview
--------

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr import NostrRAG, NostrDB

   # Initialize a Nostr database
   nostr_db = NostrDB()

   # Create a RAG agent
   rag_agent = NostrRAG(nostr_db=nostr_db)

   async def main():
       # Store a note
       await rag_agent.add_note("My first note")

       # Retrieve notes
       results = await rag_agent.query("first note")
       for result in results:
           print(result)

   if __name__ == "__main__":
       asyncio.run(main())

Reference
---------

.. automodule:: agentstr.agents.nostr_rag
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.database.base.NostrDB` — for the base class for Nostr databases.
