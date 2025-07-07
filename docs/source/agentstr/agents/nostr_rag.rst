Nostr RAG (Retrieval-Augmented Generation)
==========================================

This module provides classes for building Retrieval-Augmented Generation (RAG) agents that can store and retrieve information from the Nostr network.

Usage
-----

.. code-block:: python

   import asyncio
   from agentstr import NostrRAG
   # Note: To use NostrRAG, you must install the required dependencies:
   # pip install "agentstr-sdk[rag]"
   # You will also need an LLM API key

   # Create a RAG agent, connecting to Nostr relays and using an LLM.
   rag_agent = NostrRAG()

   async def main():
       # Ask a question. The agent will build a knowledge base from
       # recent Nostr posts related to the query and generate an answer.
       question = "What's new with AI?"
       answer = await rag_agent.query(question, limit=5)
       print(f"Question: {question}")
       print(f"Answer: {answer}")

   if __name__ == "__main__":
       asyncio.run(main())

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

`NostrRAG` uses the following environment variables by default through its underlying components:

- **NOSTR_RELAYS**: A comma-separated list of relay URLs to connect to. If not provided as a parameter, the agent will use this environment variable.
- **NOSTR_NSEC**: The Nostr private key in 'nsec' format for authenticated operations. If not provided as a parameter, the agent will look for this environment variable.
- **LLM_BASE_URL**: The base URL for the LLM API endpoint. If not provided as a parameter, the agent will use this environment variable.
- **LLM_API_KEY**: The API key for accessing the LLM service. If not provided as a parameter, the agent will use this environment variable.
- **LLM_MODEL_NAME**: The name of the LLM model to use for chat interactions. If not provided as a parameter, the agent will use this environment variable.

.. note::
   You can override these environment variables by passing explicit parameters to the `NostrRAG` constructor, such as `relays`, `private_key`, `llm_base_url`, `llm_api_key`, or `llm_model_name`.

Reference
---------

.. automodule:: agentstr.agents.nostr_rag
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.agents.nostr_rag.NostrRAG` — for the base class of Nostr RAG.
