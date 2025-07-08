Commands
========

Agents can be equipped with a command handling system that allows them to respond to specific, exclamation-prefixed messages (e.g., `!help`). The :class:`~agentstr.commands.DefaultCommands` class routes these commands to registered asynchronous handler functions. For more information on creating and managing commands, refer to :doc:`../../agentstr/commands`.

**Default Commands:**

*   `!help`: Lists available commands.
*   `!describe`: Provides a description of the agent.
*   `!balance`: Shows the user's current balance.
*   `!deposit <amount>`: Provides a deposit address for the user to top up their balance.

Relevant Modules
----------------

*   :doc:`../../agentstr/commands`
