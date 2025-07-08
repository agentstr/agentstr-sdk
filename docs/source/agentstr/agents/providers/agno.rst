Agno Agent Provider
===================

This module provides an adapter for using `Agno <https://github.com/agno-agi/agno>`_ agents with the Agentstr framework.

Overview
--------

The main component is the ``agno_agent_callable`` function, which wraps an ``agno.agent.Agent`` instance, making it compatible with the ``NostrAgent``. This allows you to leverage Agno's capabilities within the Agentstr ecosystem.

Usage
~~~~~

.. code-block:: python

   from agentstr.agents.providers.agno import agno_agent_callable
   from agentstr import NostrAgent, AgentCard
   from agno.agent import Agent
   from agno.models.openai import OpenAIChat

   # Note: To run this example, you need the Agentstr Agno extra
   # pip install agentstr-sdk[agno]

   # 1. Initialize an Agno agent (requires configuration, e.g., API keys)
   my_agno_agent = Agent(model=OpenAIChat())

   # 2. Wrap the Agno agent to create a callable compatible with Agentstr
   agent_callable = agno_agent_callable(my_agno_agent)

   # 3. Create the NostrAgent, providing the callable and an AgentCard
   agent_card = AgentCard(name="AgnoBot", description="An agent powered by Agno.")
   nostr_agent = NostrAgent(
       agent_card=agent_card,
       agent_callable=agent_callable,
   )

   # This `nostr_agent` can now be used with a NostrAgentServer to expose
   # the Agno agent over the Nostr protocol.

Reference
---------

.. automodule:: agentstr.agents.providers.agno
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../mcp/providers/agno` — For converting MCP tools to the Agno format.
- `Agno Example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/agno_agent.py>`_ - A complete example of using Agno with Agentstr.
