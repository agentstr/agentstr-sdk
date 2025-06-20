Command Dispatcher
=================

This module provides a lightweight yet powerful dispatcher for "exclamation
commands" that are commonly used in chat-based user interfaces. It converts
messages such as ``!help`` or ``!deposit 100`` into asynchronous function calls
and returns a reply via *direct message* on Nostr.

Key Features
------------

* **Prefix parsing** – Safely ignores non-command messages.
* **Pluggable callbacks** – Any ``async def`` accepting ``(command, pubkey)``
  can be registered.
* **Extensible** – Sub-class :class:`agentstr.commands.Commands` and add your
  own handlers.
* **Batteries-included defaults** – :class:`agentstr.commands.DefaultCommands`
  implements ``help``, ``describe``, ``balance`` and ``deposit`` out-of-the box.

.. automodule:: agentstr.commands
   :members:
   :undoc-members:
   :show-inheritance:
