NWC (Nostr Wallet Connect) Relay
================================

This module implements a client for interacting with Nostr Wallet Connect (NWC) relays.

Overview
--------

The ``NWCRelay`` class handles encrypted communication with wallet services over the Nostr network. It can be used to create and check invoices, make payments, and get wallet information.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.relays.nwc_relay import NWCRelay

   # Replace with your NWC connection string
   nwc_string = "nostr+walletconnect://..."

   async def main():
       nwc_relay = NWCRelay(nwc_string)
       balance = await nwc_relay.get_balance()
       print(f"Wallet balance: {balance} sats")

   if __name__ == "__main__":
       asyncio.run(main())

Reference
---------

.. automodule:: agentstr.relays.nwc_relay
   :members:
   :undoc-members:
   :show-inheritance:
