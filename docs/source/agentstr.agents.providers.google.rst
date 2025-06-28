Google Agent Provider
=====================

This module provides adapters for using Google's agent development tools with the Agentstr framework.

Overview
--------

The main components are the ``google_agent_callable`` and ``google_chat_generator`` functions, which wrap a ``google.adk.agents.Agent`` instance, making it compatible with the ``NostrAgent``. This allows you to leverage Google's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.google import google_chat_generator
   from agentstr import NostrAgent
   from google.adk.agents import Agent
   from google.adk.models.lite_llm import LiteLlm

   # Assume 'my_google_agent' is an initialized Google agent
   my_google_agent = Agent(model=LiteLlm())

   chat_generator = google_chat_generator(my_google_agent)

   nostr_agent = NostrAgent(
       chat_generator=chat_generator,
       # ... other NostrAgent config
   )

Reference
---------

.. automodule:: agentstr.agents.providers.google
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.mcp.providers.google` — For converting MCP tools to the Google format.
