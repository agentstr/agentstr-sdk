Google Agent Provider
=====================

This module provides adapters for using Google's agent development tools with the Agentstr framework.

Overview
--------

The main components are the ``google_agent_callable`` and ``google_chat_generator`` functions, which wrap a ``google.adk.agents.Agent`` instance, making it compatible with the ``NostrAgent``. This allows you to leverage Google's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.google import google_chat_generator
   from agentstr import NostrAgent, AgentCard
   from google.adk.agents import Agent
   from google.adk.models.lite_llm import LiteLlm

   # Note: To run this example, you need the Google Agent Development Kit installed
   # and your environment configured (e.g., with a GOOGLE_API_KEY).
   # pip install google-adk google-generativeai

   # 1. Initialize a Google agent
   # This example uses LiteLlm, which may require further configuration.
   my_google_agent = Agent(model=LiteLlm())

   # 2. Wrap the Google agent to create a streaming generator for Agentstr
   chat_generator = google_chat_generator(my_google_agent)

   # 3. Create the NostrAgent, providing the generator and an AgentCard
   agent_card = AgentCard(name="GoogleBot", description="An agent powered by Google ADK.")
   nostr_agent = NostrAgent(
       agent_card=agent_card,
       chat_generator=chat_generator,
   )

   # This `nostr_agent` can now be used with a NostrAgentServer.

Reference
---------

.. automodule:: agentstr.agents.providers.google
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.mcp.providers.google` — For converting MCP tools to the Google format.
