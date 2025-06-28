Command Dispatcher
==================

This module provides a lightweight yet powerful dispatcher for "exclamation
commands" that are commonly used in chat-based user interfaces. It converts
messages such as ``!help`` or ``!deposit 100`` into asynchronous function calls
and returns a reply via *direct message* on Nostr.

Overview
--------

The ``CommandDispatcher`` class allows you to register functions as commands and then dispatch incoming messages to the appropriate function.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.commands import CommandDispatcher, command

   # Create a dispatcher instance
   dispatcher = CommandDispatcher()

   # Define a command
   @command(dispatcher)
   async def help(arg: str):
       """Provides help for a command."""
       return f"Help for {arg}"

   # Dispatch a command
   async def main():
       result = await dispatcher.dispatch("!help topic")
       print(result)

   asyncio.run(main())

Reference
---------

.. automodule:: agentstr.commands
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.agents.nostr_agent.NostrAgent` — which can use the dispatcher to handle commands.
