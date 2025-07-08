OpenAI Agent Provider
=====================

This module provides an adapter for using `OpenAI Agents SDK <https://openai.github.io/openai-agents-python/>`_ with the Agentstr framework.

Overview
--------

The main component is the ``openai_agent_callable`` function, which wraps an ``agents.Agent`` instance, making it compatible with the ``NostrAgent``. This allows you to leverage OpenAI's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.openai import openai_agent_callable
   from agentstr import NostrAgent, AgentCard
   from agents import Agent
   from agents.models import OpenAIChatCompletionsModel
   from openai import AsyncOpenAI

   # Note: To run this example, you need the Agentstr OpenAI extra
   # pip install agentstr-sdk[openai]

   # 1. Initialize an OpenAI client (requires OPENAI_API_KEY in env)
   client = AsyncOpenAI()

   # 2. Create an agent using the 'agents' library
   my_openai_agent = Agent(
       model=OpenAIChatCompletionsModel(
           model="gpt-4-turbo",
           openai_client=client
       )
   )

   # 3. Wrap the agent to create a callable for Agentstr
   agent_callable = openai_agent_callable(my_openai_agent)

   # 4. Create the NostrAgent, providing the callable and an AgentCard
   agent_card = AgentCard(name="OpenAIBot", description="An agent powered by OpenAI.")
   nostr_agent = NostrAgent(
       agent_card=agent_card,
       agent_callable=agent_callable,
   )

   # This `nostr_agent` can now be used with a NostrAgentServer.

Reference
---------

.. automodule:: agentstr.agents.providers.openai
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../mcp/providers/openai` — For converting MCP tools to the OpenAI format.
- `OpenAI Example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/openai_agent.py>`_ - A complete example of using OpenAI with Agentstr.
