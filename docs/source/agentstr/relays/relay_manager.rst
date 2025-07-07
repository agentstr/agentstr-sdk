Relay Manager
=============

This module provides a management layer for handling multiple Nostr relay connections.

Overview
--------

The ``RelayManager`` class manages connections to multiple Nostr relays, handling message passing, event fetching, and event publishing across all of them.

**Typical usage:**

.. code-block:: python

   import asyncio
   from pynostr.key import PrivateKey
   from pynostr.filters import Filters
   from agentstr.relays.relay_manager import RelayManager

   async def main():
       # A list of public relays
       relay_urls = ["wss://relay.damus.io", "wss://relay.primal.net"]

       # Generate a new private key for demonstration
       private_key = PrivateKey()

       # Initialize the RelayManager
       relay_manager = RelayManager(relay_urls, private_key)

       # Create filters to fetch recent text notes
       filters = Filters(kinds=[1], limit=5)

       # Fetch events from all relays
       events = await relay_manager.get_events(filters)

       if events:
           print(f"Fetched {len(events)} unique events from {len(relay_urls)} relays:")
           for event in events:
               print(f" - Event content: {event.content}")
       else:
           print("No events found.")

   if __name__ == "__main__":
       asyncio.run(main())

Reference
---------

.. automodule:: agentstr.relays.relay_manager
   :members:
   :undoc-members:
   :show-inheritance:
