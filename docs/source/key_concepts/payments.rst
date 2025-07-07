Payments
========

Agentstr has built-in support for handling payments via the Nostr Wallet Connect (NWC) protocol. The :class:`~agentstr.relays.nwc_relay.NWCRelay` class provides an interface for sending and receiving payments.

To integrate payment processing into your agent, you'll need to configure the NWC relay. Refer to :doc:`../../agentstr.relays` for setup instructions.

Payments are also integrated with Nostr MCP servers to enable paid tools, allowing agents to pay for premium services and fairly charge the cost back to the user.

Next Steps
----------

- **Enable Payments in Agents**: Learn how to integrate NWC with agents in the :doc:`../getting_started/payment_enabled_agent` guide.
- **Paid Tools with MCP**: See how to use NWC for paid tools in MCP servers in the :doc:`../getting_started/creating_an_mcp_server` guide.

Relevant Modules
----------------

*   :doc:`../../agentstr.relays.nwc_relay`
