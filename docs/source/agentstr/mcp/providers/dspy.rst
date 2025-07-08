DSPy MCP Provider
====================

This module provides integration with `DSPy <https://dspy.ai/>`_, allowing conversion between MCP tools and DSPy's tool format.

Overview
--------

The primary function in this module is ``to_dspy_tools``, which takes a ``NostrMCPClient`` instance and converts the available MCP tools into a format that can be used by a DSPy agent (like ``dspy.ReAct``).

Usage
~~~~~

.. code-block:: python

   import dspy
   from agentstr.mcp.providers.dspy import to_dspy_tools
   from agentstr.mcp.nostr_mcp_client import NostrMCPClient

   # Assume nostr_mcp_client is an initialized and connected NostrMCPClient
   async def setup_dspy_agent(nostr_mcp_client: NostrMCPClient):
       # Convert MCP tools to DSPy format
       dspy_tools = await to_dspy_tools(nostr_mcp_client)

       # Create a DSPy agent with the converted tools
       agent = dspy.ReAct("question -> answer: str", tools=dspy_tools)
       return agent

.. note::
   For a complete, working example, check out the `DSPy Agent example <https://github.com/agentstr/agentstr-sdk/blob/main/examples/dspy_agent.py>`_.

Reference
---------

.. automodule:: agentstr.mcp.providers.dspy
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../agents/providers/dspy` — For using DSPy agents with Agentstr.
- :class:`agentstr.mcp.nostr_mcp_client.NostrMCPClient` — The client used to fetch MCP tools.

