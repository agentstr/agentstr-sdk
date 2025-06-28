PydanticAI Agent Provider
=========================

This module provides an adapter for using `PydanticAI <https://github.com/pydantic/pydantic-ai>`_ agents with the Agentstr framework.

Overview
--------

The main component is the ``pydantic_agent_callable`` function, which wraps a ``pydantic_ai.Agent`` instance, making it compatible with the ``NostrAgent``. This allows you to leverage PydanticAI's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.pydantic import pydantic_agent_callable
   from agentstr import NostrAgent
   from pydantic_ai import Agent
   from pydantic_ai.models.openai import OpenAIModel

   # Assume 'my_pydantic_agent' is an initialized PydanticAI agent
   my_pydantic_agent = Agent(model=OpenAIModel("gpt-4-turbo"))

   agent_callable = pydantic_agent_callable(my_pydantic_agent)

   nostr_agent = NostrAgent(
       agent_callable=agent_callable,
       # ... other NostrAgent config
   )

Reference
---------

.. automodule:: agentstr.agents.providers.pydantic
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.mcp.providers.pydantic` — For converting MCP tools to the PydanticAI format.
