Command Dispatcher
==================

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

**Typical usage:**

.. code-block:: python

   import asyncio
   import os
   from agentstr.database import SQLiteDatabase
   from agentstr.commands import DefaultCommands
   from agentstr import AgentCard, NostrClient, NostrAgentServer

   # This example requires a server private key (NSEC) to be set as an
   # environment variable (e.g., in a .env file).

   async def main():
       # 1. Configuration
       relays = os.getenv("NOSTR_RELAYS", "ws://localhost:8080").split(",")
       private_key = os.getenv("SERVER_PRIVATE_KEY")

       if not private_key:
           print("Error: SERVER_PRIVATE_KEY environment variable is not set.")
           return

       # 2. Initialize core components
       nostr_client = NostrClient(relays=relays, private_key=private_key)
       server_pubkey = nostr_client.public_key_hex

       agent_card = AgentCard(
           name="CommandsAgent",
           description="An agent that responds to !help, !balance, etc.",
           nostr_pubkey=server_pubkey
       )

       db = await SQLiteDatabase(conn_str="sqlite://:memory:").async_init()

       # 3. Set up the command dispatcher with default commands
       commands = DefaultCommands(
           db=db,
           nostr_client=nostr_client,
           agent_card=agent_card
       )

       # 4. Create and start the agent server
       agent_server = NostrAgentServer(
           nostr_client=nostr_client,
           agent_card=agent_card,
           commands=commands
       )

       print(f"Agent server starting with pubkey: {server_pubkey}")
       # The server runs indefinitely, listening for commands.
       await agent_server.start()

   if __name__ == "__main__":
       # To run this, save it as a Python file, set the required
       # environment variable, and then execute the script.
       # asyncio.run(main())
       pass

Reference
---------

.. automodule:: agentstr.commands
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.agents.nostr_agent.NostrAgent` — which can use the dispatcher to handle commands.
