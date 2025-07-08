PydanticAI Agent Provider
=========================

This module provides an adapter for using `PydanticAI <https://ai.pydantic.dev/>`_ agents with the Agentstr framework.

Overview
--------

The main component is the ``pydantic_agent_callable`` function, which wraps a ``pydantic_ai.Agent`` instance, making it compatible with the ``NostrAgent``. This allows you to leverage PydanticAI's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.pydantic import pydantic_agent_callable
   from agentstr import NostrAgent, AgentCard
   from pydantic_ai import Agent
   from pydantic_ai.llm.openai import OpenAI

   # Note: To run this example, you need the Agentstr Pydantic extra
   # pip install agentstr-sdk[pydantic]

   # 1. Initialize a PydanticAI agent with an LLM
   # This example uses the OpenAI LLM.
   llm = OpenAI()
   my_pydantic_agent = Agent(llm=llm)

   # 2. Wrap the agent to create a callable for Agentstr
   agent_callable = pydantic_agent_callable(my_pydantic_agent)

   # 3. Create the NostrAgent, providing the callable and an AgentCard
   agent_card = AgentCard(name="PydanticBot", description="An agent powered by PydanticAI.")
   nostr_agent = NostrAgent(
       agent_card=agent_card,
       agent_callable=agent_callable,
   )

   # This `nostr_agent` can now be used with a NostrAgentServer.

Reference
---------

.. automodule:: agentstr.agents.providers.pydantic
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../mcp/providers/pydantic` — For converting MCP tools to the PydanticAI format.
- `PydanticAI Example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/pydantic_agent.py>`_ - A complete example of using PydanticAI with Agentstr.

