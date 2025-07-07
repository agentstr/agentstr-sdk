DSPy Agent Provider
===================

This module provides an adapter for using `DSPy <https://dspy.ai/>`_ agents with the Agentstr framework.

Overview
--------

The main component is the ``dspy_agent_callable`` function, which wraps a DSPy module (like ``dspy.ReAct``), making it compatible with the ``NostrAgent``. This allows you to leverage DSPy's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.dspy import dspy_agent_callable
   from agentstr import NostrAgent, AgentCard
   import dspy

   # Note: To run this example, you need DSPy and an LLM provider installed,
   # and your environment configured (e.g., with an OPENAI_API_KEY).
   # pip install dspy-ai openai

   # 1. Configure DSPy with a language model
   lm = dspy.OpenAI(model='gpt-3.5-turbo')
   dspy.settings.configure(lm=lm)

   # 2. Initialize a DSPy module (e.g., a ReAct agent)
   # The signature defines the input ('question') and output ('answer') fields.
   my_dspy_agent = dspy.ReAct(signatures="question -> answer")

   # 3. Wrap the DSPy module to create a callable compatible with Agentstr
   agent_callable = dspy_agent_callable(my_dspy_agent)

   # 4. Create the NostrAgent, providing the callable and an AgentCard
   agent_card = AgentCard(name="DSPyBot", description="An agent powered by DSPy.")
   nostr_agent = NostrAgent(
       agent_card=agent_card,
       agent_callable=agent_callable,
   )

   # This `nostr_agent` can now be used with a NostrAgentServer.

Reference
---------

.. automodule:: agentstr.agents.providers.dspy
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../mcp/providers/dspy` — For converting MCP tools to the DSPy format.
