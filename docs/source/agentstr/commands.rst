Commands
========

This module provides utility classes for parsing and handling exclamation-prefixed commands (e.g., ``!help``) commonly used by chat bots and conversational agents on Nostr.

Overview
--------

The module features two main classes:

- ``Commands``: A lightweight, generic dispatcher that routes incoming commands to registered asynchronous handler functions. It provides a base for creating custom command sets.

- ``DefaultCommands``: A concrete implementation of ``Commands`` that includes a useful set of built-in commands for most agents:

  - ``!help``: Lists all available commands.
  - ``!describe``: Shows the agent's name and description.
  - ``!balance``: Returns the user's current satoshi balance.
  - ``!deposit [amount]``: Creates a Nostr Wallet Connect (NWC) invoice to allow users to top up their balance.

- If the default commands are not sufficient, you can create your own by subclassing the ``Commands`` class and registering your own command handlers.

Customizing Commands
--------------------




Reference
---------

.. automodule:: agentstr.commands
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.agents.nostr_agent.NostrAgent` — which can use the dispatcher to handle commands.
