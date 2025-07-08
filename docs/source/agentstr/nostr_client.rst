Nostr Client
============

This document explains the `NostrClient` class from the Agentstr SDK, which is the high-level client used to interact with the Nostr network.

Overview of NostrClient
-----------------------

The `NostrClient` class provides the core functionality for connecting to Nostr relays, sending and receiving messages, and managing a Nostr identity. It is a foundational component for building agents and MCP servers in Agentstr.

Key Features
~~~~~~~~~~~~

- **Relay Connection**: Connects to specified Nostr relays for network communication.
- **Identity Management**: Supports both read-only mode and authenticated mode with a private key.
- **Message Handling**: Sends and receives direct messages and other events on the Nostr network.
- **Wallet Integration**: Supports Nostr Wallet Connect (NWC) for payment processing.

Initialization
~~~~~~~~~~~~~~

The `NostrClient` can be initialized with default values from environment variables or with explicit parameters to override them.

.. code-block:: python

   from agentstr import NostrClient

   # Initialize with default environment variables
   client = NostrClient()

   # Or override defaults with explicit parameters
   # But please do not hardcode your private key in production code
   client = NostrClient(
       relays=["wss://relay.example.com"],
       private_key="nsec1...your-private-key...",
       nwc_str="nostr+walletconnect://...your-connection-string..."
   )

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

`NostrClient` uses the following environment variables by default:

- **NOSTR_RELAYS**: A comma-separated list of relay URLs to connect to. If not provided as a parameter, the client will use this environment variable. If neither is provided, initialization will fail.
- **NOSTR_NSEC**: The Nostr private key in 'nsec' format for authenticated operations. If not provided as a parameter, the client will look for this environment variable. If neither is provided, the client operates in read-only mode.
- **NWC_CONN_STR**: The Nostr Wallet Connect string for payment processing. If not provided as a parameter, the client will use this environment variable. If neither is provided, NWC will not be enabled.

.. note::
   You can override these environment variables by passing explicit parameters to the `NostrClient` constructor. For example, passing a `relays` list will ignore `NOSTR_RELAYS`, and passing `private_key` will ignore `NOSTR_NSEC`.

Usage Example
~~~~~~~~~~~~~

.. code-block:: python

   from agentstr import NostrClient

   # Initialize client with defaults from environment variables
   client = NostrClient()

   # Main function
   async def main():
      # Retrieve metadata for a public key
      metadata = await client.get_metadata_for_pubkey("npub1...your-public-key...")
      print(metadata)

   if __name__ == "__main__":
      asyncio.run(main())


Reference
---------

.. automodule:: agentstr.nostr_client
   :members:
   :undoc-members:
   :show-inheritance: