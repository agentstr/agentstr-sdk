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

- If the default commands are sufficient, Agentstr will automatically wire them up for you.

- If the default commands are not sufficient, you can create your own by subclassing the ``Commands`` class and registering your own command handlers.

Customizing Commands
--------------------

Here is an example of adding custom commands to an agent. The following example shows how to add a custom command called ``!custom`` that sends a message back to the user.

.. code-block:: python

    # Override DefaultCommands to add a custom command
    class CustomCommands(DefaultCommands):
        def __init__(self):
            super().__init__()
            self.commands.update({
                "custom": self._custom,
            })
            print(f'Commands: {self.commands}')
        
        # Custom command handler (invoked when user sends "!custom")
        async def _custom(self, command: str, pubkey: str):        
            await self.nostr_client.send_direct_message(pubkey, "Custom command received!")

.. note::
   For a complete, working example, check out the `Custom Commands example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/custom_commands.py>`_.

Reference
---------

.. automodule:: agentstr.commands.base
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: agentstr.commands.commands
   :members:
   :undoc-members:
   :show-inheritance:


See Also
--------
- :class:`agentstr.agents.nostr_agent.NostrAgentServer` — which intercepts and processes incoming commands from Nostr messages.
