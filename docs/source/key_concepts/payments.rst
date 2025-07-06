Payments
========

`agentstr` has built-in support for handling payments via the Nostr Wallet Connect (NWC) protocol. The :class:`~agentstr.relays.nwc_relay.NWCRelay` class provides an interface for sending and receiving payments.

To integrate payment processing into your agent, you'll need to configure the NWC relay. Refer to :doc:`../../agentstr.relays` for setup instructions.

This is integrated with the MCP server to allow for paid tools, where an agent can pay for tools and charge for the use of its services.

Relevant Modules
----------------

*   :doc:`../../agentstr.relays`
