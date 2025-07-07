Nostr Wallet Connect Relay
==========================

This document explains the `NWCRelay` class from the Agentstr SDK, which handles encrypted communication with wallet services over the Nostr network for payment processing.

Overview of NWCRelay
--------------------

The `NWCRelay` class is used to integrate Nostr Wallet Connect (NWC) functionality into Agentstr agents and MCP servers. It enables payment processing by communicating with wallet services through encrypted messages on the Nostr network.

Key Features
------------

- **Payment Processing**: Facilitates sending and receiving payments via Nostr Wallet Connect.
- **Encrypted Communication**: Uses encrypted direct messages to securely interact with wallet services.

Initialization
--------------

The `NWCRelay` can be initialized with a connection string directly or can use a default environment variable.

.. code-block:: python

   from agentstr.relays.nwc_relay import NWCRelay

   # Initialize with default environment variable
   nwc_relay = NWCRelay()

   # Or override with explicit connection string
   nwc_relay = NWCRelay(nwc_connection_string="nostr+walletconnect://...your-connection-string...")

Environment Variables
---------------------

`NWCRelay` uses the following environment variable by default:

- **NWC_CONN_STR**: The Nostr Wallet Connect string for payment processing. If not provided as a parameter, the relay will use this environment variable. If neither is provided, initialization will fail with an error.

.. note::
   You can override this environment variable by passing an explicit `nwc_connection_string` parameter to the `NWCRelay` constructor.

Next Steps
----------

- **Enable Payments in Agents**: Learn how to integrate NWC with agents in the :doc:`../getting_started/payment_enabled_agent` guide.
- **Paid Tools with MCP**: See how to use NWC for paid tools in MCP servers in the :doc:`../getting_started/creating_an_mcp_server` guide.

Reference
---------

.. automodule:: agentstr.relays.nwc_relay
   :members:
   :undoc-members:
   :show-inheritance:
