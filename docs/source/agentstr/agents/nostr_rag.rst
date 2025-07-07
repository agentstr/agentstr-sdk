Nostr RAG (Retrieval-Augmented Generation)
==========================================

This module provides classes for building Retrieval-Augmented Generation (RAG) agents that can store and retrieve information from the Nostr network.

Overview
--------

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr import NostrRAG
   # Note: To use NostrRAG, you must install the required dependencies:
   # pip install "agentstr-sdk[rag]"
   # You will also need an OpenAI API key or another LangChain-compatible LLM.
   from langchain_openai import ChatOpenAI

   # Create a RAG agent, connecting to Nostr relays and using an LLM.
   rag_agent = NostrRAG(
       relays=["wss://relay.damus.io"],
       llm=ChatOpenAI(model_name="gpt-3.5-turbo")
   )

   async def main():
       # Ask a question. The agent will build a knowledge base from
       # recent Nostr posts related to the query and generate an answer.
       question = "What are people saying about the bitcoin price?"
       answer = await rag_agent.query(question, limit=10)
       print(f"Question: {question}")
       print(f"Answer: {answer}")

   if __name__ == "__main__":
       asyncio.run(main())

Reference
---------

.. automodule:: agentstr.agents.nostr_rag
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :class:`agentstr.database.base.NostrDB` — for the base class for Nostr databases.
