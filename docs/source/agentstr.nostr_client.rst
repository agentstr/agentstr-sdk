Nostr Client
============

This module provides a client for interacting with the Nostr protocol, handling events, direct messages, and metadata.

Overview
--------

The ``NostrClient`` class provides methods to connect to Nostr relays, send and receive direct messages, manage metadata, and read posts by tags. It integrates with Nostr Wallet Connect (NWC) for payment processing if provided.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr import NostrClient

   relays = ["wss://relay.damus.io"]
   client = NostrClient(relays)

   async def main():
       events = await client.read_posts_by_tag("agentstr_agents", limit=5)
       for ev in events:
           print(ev.content)

   asyncio.run(main())

Reference
---------

.. automodule:: agentstr.nostr_client
   :members:
   :undoc-members:
   :show-inheritance:
