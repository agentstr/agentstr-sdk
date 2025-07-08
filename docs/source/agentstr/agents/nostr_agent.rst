Nostr Agent
===========

This document explains the `NostrAgent` class from the Agentstr SDK, which is used to create agents that interact with the Nostr network.

Overview of NostrAgent
----------------------

The `NostrAgent` class is a core component of the Agentstr SDK, allowing developers to build conversational agents that operate on the Nostr network. It integrates with language models (LLMs) for chat functionality and supports payment processing through Nostr Wallet Connect.

Key Features
~~~~~~~~~~~~

- **Conversational Interface**: Processes user input and generates responses using a common chat interface.
- **Nostr Integration**: Connects to the Nostr network for decentralized communication.
- **Payment Support**: Can charge for interactions or pay for tool usage with Nostr Wallet Connect.
- **Human-in-the-Loop**: Can confirm tool calls and delegate tool payments to a human (or other agent).
- **State Persistence**: Can store and retrieve user information and message history using a database.
- **Metadata**: Supports broadcasting agent metadata for discoverability on the Nostr network.

Usage
-----

The `NostrAgent` can be initialized with various parameters, leveraging defaults from environment variables where available.

.. code-block:: python

   from agentstr import NostrAgent, AgentCard, ChatInput, ChatOutput

   # Define an agent card with metadata
   agent_card = AgentCard(name="MyAgent", description="A helpful chat agent")

   # Define a chat generator function
   async def chat_generator(input: ChatInput):
       yield ChatOutput(message=f"Echo: {input.message}")

   # Initialize using environment variable defaults
   agent = NostrAgent(agent_card=agent_card, chat_generator=chat_generator)

.. note::
   See :doc:`nostr_agent_server` for information on how to run the agent.


Environment Variables
~~~~~~~~~~~~~~~~~~~~~

`NostrAgent` uses the following environment variables by default through its underlying components:

- **NOSTR_RELAYS**: A comma-separated list of relay URLs to connect to. If not provided as a parameter, the agent will use this environment variable.
- **NOSTR_NSEC**: The Nostr private key in 'nsec' format for authenticated operations. If not provided as a parameter, the agent will look for this environment variable.
- **NWC_CONN_STR**: The Nostr Wallet Connect string for payment processing. If not provided as a parameter, the agent will use this environment variable.
- **LLM_BASE_URL**: The base URL for the LLM API endpoint. If not provided as a parameter, the agent will use this environment variable.
- **LLM_API_KEY**: The API key for accessing the LLM service. If not provided as a parameter, the agent will use this environment variable.
- **LLM_MODEL_NAME**: The name of the LLM model to use for chat interactions. If not provided as a parameter, the agent will use this environment variable.

.. note::
   You can override these environment variables by passing explicit parameters to the `NostrAgent` constructor, such as `relays`, `private_key`, `nwc_str`, `llm_base_url`, `llm_api_key`, or `llm_model_name`.

Reference
---------

.. automodule:: agentstr.agents.nostr_agent
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`../../getting_started/simple_agent` — for running an agent with the high-level `AgentstrAgent` class.
- :doc:`../../getting_started/payment_enabled_agent` — for adding payment processing to your agent.
- :doc:`../../key_concepts/nostr_metadata` — for enhancing your agent's visibility with metadata.