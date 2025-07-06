Nostr Client
============

This document explains the `NostrClient` class from the Agentstr SDK, which is used to interact with the Nostr network.

Overview of NostrClient
-----------------------

The `NostrClient` class provides the core functionality for connecting to Nostr relays, sending and receiving messages, and managing a Nostr identity. It is a foundational component for building agents and MCP servers in Agentstr.

Key Features
------------

- **Relay Connection**: Connects to specified Nostr relays for network communication.
- **Identity Management**: Supports both read-only mode and authenticated mode with a private key.
- **Message Handling**: Sends and receives direct messages and other events on the Nostr network.
- **Wallet Integration**: Supports Nostr Wallet Connect (NWC) for payment processing.

Initialization
--------------

The `NostrClient` can be initialized with default values from environment variables or with explicit parameters to override them.

.. code-block:: python

   from agentstr import NostrClient

   # Initialize with default environment variables
   client = NostrClient()

   # Or override defaults with explicit parameters
   client = NostrClient(
       relays=["wss://relay.example.com"],
       private_key="nsec1...your-private-key...",
       nwc_str="nostr+walletconnect://...your-connection-string..."
   )

Environment Variables
---------------------

`NostrClient` uses the following environment variables by default:

- **NOSTR_RELAYS**: A comma-separated list of relay URLs to connect to. If not provided as a parameter, the client will use this environment variable. If neither is provided, initialization will fail.
- **NOSTR_NSEC**: The Nostr private key in 'nsec' format for authenticated operations. If not provided as a parameter, the client will look for this environment variable. If neither is provided, the client operates in read-only mode.
- **NWC_CONN_STR**: The Nostr Wallet Connect string for payment processing. If not provided as a parameter, the client will use this environment variable. If neither is provided, NWC will not be enabled.

.. note::
   You can override these environment variables by passing explicit parameters to the `NostrClient` constructor. For example, passing a `relays` list will ignore `NOSTR_RELAYS`, and passing `private_key` will ignore `NOSTR_NSEC`.

Usage Example
-------------

.. code-block:: python

   from agentstr import NostrClient
   import os

   # Set environment variables (or use .env file)
   os.environ["NOSTR_RELAYS"] = "wss://relay.damus.io,wss://relay.primal.net"
   os.environ["NOSTR_NSEC"] = "nsec1...your-private-key..."
   os.environ["NWC_CONN_STR"] = "nostr+walletconnect://...your-connection-string..."

   # Initialize client with defaults from environment variables
   client = NostrClient()

   # Use the client for agent or MCP server operations
   print(f"Initialized with public key: {client.public_key.bech32()}")

Next Steps
----------

- **Build an Agent**: Learn how to use `NostrClient` with `NostrAgent` in the :doc:`../getting_started/simple_agent` guide.
- **Create an MCP Server**: See how to integrate `NostrClient` with `NostrMCPServer` in the :doc:`../getting_started/creating_an_mcp_server` guide.
- **Explore NWC**: Dive into payment processing with Nostr Wallet Connect in the :doc:`../getting_started/payment_enabled_agent` guide.

Reference
---------

.. automodule:: agentstr.nostr_client
   :members:
   :undoc-members:
   :show-inheritance:
