OpenAI Agent Provider
=====================

This module provides an adapter for using OpenAI-compatible agents with the Agentstr framework.

Overview
--------

The main component is the ``openai_agent_callable`` function, which wraps an ``agents.Agent`` instance, making it compatible with the ``NostrAgent``. This allows you to leverage OpenAI's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.openai import openai_agent_callable
   from agentstr import NostrAgent
   from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI

   # Assume 'my_openai_agent' is an initialized OpenAI-compatible agent
   my_openai_agent = Agent(model=OpenAIChatCompletionsModel(model="gpt-4-turbo", openai_client=AsyncOpenAI()))

   agent_callable = openai_agent_callable(my_openai_agent)

   nostr_agent = NostrAgent(
       agent_callable=agent_callable,
       # ... other NostrAgent config
   )

Reference
---------

.. automodule:: agentstr.agents.providers.openai
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.mcp.providers.openai` — For converting MCP tools to the OpenAI format.
