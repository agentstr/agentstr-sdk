DSPy Agent Provider
===================

This module provides an adapter for using `DSPy <https://github.com/stanford-futuredata/dspy>`_ agents with the Agentstr framework.

Overview
--------

The main component is the ``dspy_agent_callable`` function, which wraps a DSPy module (like ``dspy.ReAct``), making it compatible with the ``NostrAgent``. This allows you to leverage DSPy's capabilities within the Agentstr ecosystem.

**Typical usage:**

.. code-block:: python

   from agentstr.agents.providers.dspy import dspy_agent_callable
   from agentstr import NostrAgent
   import dspy

   # Assume 'my_dspy_agent' is an initialized DSPy agent
   my_dspy_agent = dspy.ReAct("question -> answer: str")

   agent_callable = dspy_agent_callable(my_dspy_agent)

   nostr_agent = NostrAgent(
       agent_callable=agent_callable,
       # ... other NostrAgent config
   )

Reference
---------

.. automodule:: agentstr.agents.providers.dspy
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.mcp.providers.dspy` — For converting MCP tools to the DSPy format.
