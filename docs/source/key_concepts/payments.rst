Payments
========

Agentstr has built-in support for handling payments via the Nostr Wallet Connect (NWC) protocol. The :class:`~agentstr.relays.nwc_relay.NWCRelay` class provides an interface for sending and receiving payments.

To integrate payment processing into your agent, you'll need to configure the NWC relay. Refer to :doc:`../../agentstr.relays` for setup instructions.

Payments are also integrated with Nostr MCP servers to enable paid tools, allowing agents to pay for premium services and fairly charge the cost back to the user.

Relevant Modules
----------------

*   :doc:`../../agentstr.relays.nwc_relay`
