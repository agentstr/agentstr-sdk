Agno Agent Provider
===================

This module provides an adapter for using `Agno <https://github.com/agnoauth/agno>`_ agents with the Agentstr framework.

Overview
--------

The main component is the ``agno_agent_callable`` function, which wraps an ``agno.agent.Agent`` instance, making it compatible with the ``NostrAgent``. This allows you to leverage Agno's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.agno import agno_agent_callable
   from agentstr import NostrAgent
   from agno.agent import Agent
   from agno.models.openai import OpenAIChat

   # Assume 'my_agno_agent' is an initialized Agno agent
   my_agno_agent = Agent(model=OpenAIChat())

   agent_callable = agno_agent_callable(my_agno_agent)

   nostr_agent = NostrAgent(
       agent_callable=agent_callable,
       # ... other NostrAgent config
   )

Reference
---------

.. automodule:: agentstr.agents.providers.agno
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.mcp.providers.agno` — For converting MCP tools to the Agno format.
