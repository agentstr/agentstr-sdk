Relay
=====

This module provides the core relay functionality for the Agentstr SDK.

Overview
--------

The ``EventRelay`` class handles communication with a single Nostr relay. It can be used to fetch events, send events, and listen for direct messages.

**Typical usage:**

.. code-block:: python

   import asyncio
   from pynostr.key import PrivateKey
   from pynostr.filters import Filters
   from agentstr.relays.relay import EventRelay

   async def main():
       # Use a real relay
       relay_url = "wss://relay.damus.io"

       # Generate a new private key for demonstration
       private_key = PrivateKey()

       # Initialize the EventRelay
       event_relay = EventRelay(relay_url, private_key)

       # Create filters to fetch recent text notes
       filters = Filters(kinds=[1], limit=5)

       # Fetch events
       events = await event_relay.get_events(filters)

       if events:
           print(f"Fetched {len(events)} events:")
           for event in events:
               print(f" - Event content: {event.content[:80]}...")
       else:
           print("No events found.")

   if __name__ == "__main__":
       asyncio.run(main())

Reference
---------

.. automodule:: agentstr.relays.relay
   :members:
   :undoc-members:
   :show-inheritance:
