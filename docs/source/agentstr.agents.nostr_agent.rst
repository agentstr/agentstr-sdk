Nostr Agent
===========

This document explains the `NostrAgent` class from the Agentstr SDK, which is used to create agents that interact with the Nostr network.

Overview of NostrAgent
----------------------

The `NostrAgent` class is a core component of the Agentstr SDK, allowing developers to build conversational agents that operate on the Nostr network. It integrates with language models (LLMs) for chat functionality and supports payment processing through Nostr Wallet Connect.

Key Features
------------

- **Conversational Interface**: Processes user input and generates responses using an LLM.
- **Nostr Integration**: Connects to the Nostr network for decentralized communication.
- **Payment Support**: Can charge for interactions or pay for tool usage with Nostr Wallet Connect.
- **Metadata**: Supports broadcasting agent metadata for discoverability on the Nostr network.

Initialization
--------------

The `NostrAgent` can be initialized with various parameters, leveraging defaults from environment variables where available.

.. code-block:: python

   from agentstr import NostrAgent, AgentCard

   # Define an agent card with metadata
   agent_card = AgentCard(name="MyAgent", description="A helpful chat agent")

   # Initialize with minimal parameters, using environment variable defaults
   agent = NostrAgent(agent_card=agent_card)

   # Or override defaults with explicit parameters
   agent = NostrAgent(
       agent_card=agent_card,
       relays=["wss://relay.example.com"],
       private_key="nsec1...your-private-key...",
       nwc_str="nostr+walletconnect://...your-connection-string...",
       llm_base_url="https://api.openai.com/v1",
       llm_api_key="your-api-key",
       llm_model_name="gpt-3.5-turbo"
   )

Environment Variables
---------------------

`NostrAgent` uses the following environment variables by default through its underlying components:

- **NOSTR_RELAYS**: A comma-separated list of relay URLs to connect to. If not provided as a parameter, the agent will use this environment variable.
- **NOSTR_NSEC**: The Nostr private key in 'nsec' format for authenticated operations. If not provided as a parameter, the agent will look for this environment variable.
- **NWC_CONN_STR**: The Nostr Wallet Connect string for payment processing. If not provided as a parameter, the agent will use this environment variable.
- **LLM_BASE_URL**: The base URL for the LLM API endpoint. If not provided as a parameter, the agent will use this environment variable.
- **LLM_API_KEY**: The API key for accessing the LLM service. If not provided as a parameter, the agent will use this environment variable.
- **LLM_MODEL_NAME**: The name of the LLM model to use for chat interactions. If not provided as a parameter, the agent will use this environment variable.

.. note::
   You can override these environment variables by passing explicit parameters to the `NostrAgent` constructor, such as `relays`, `private_key`, `nwc_str`, `llm_base_url`, `llm_api_key`, or `llm_model_name`.

Usage Example
-------------

.. code-block:: python

   import asyncio
   from agentstr import NostrAgent, AgentCard, ChatInput, ChatOutput
   import os

   # Set environment variables (or use .env file)
   os.environ["NOSTR_RELAYS"] = "wss://relay.damus.io,wss://relay.primal.net"
   os.environ["NOSTR_NSEC"] = "nsec1...your-private-key..."
   os.environ["NWC_CONN_STR"] = "nostr+walletconnect://...your-connection-string..."
   os.environ["LLM_BASE_URL"] = "https://api.openai.com/v1"
   os.environ["LLM_API_KEY"] = "your-api-key"
   os.environ["LLM_MODEL_NAME"] = "gpt-3.5-turbo"

   # Define a simple chat function
   async def simple_chat(input: ChatInput):
       yield ChatOutput(message=f"Echo: {input.message}")

   # Create agent card and agent
   agent_card = AgentCard(name="EchoBot", description="Echoes your input")
   nostr_agent = NostrAgent(agent_card=agent_card, chat_generator=simple_chat)

   # Start the agent (typically done through NostrAgentServer)
   print(f"Agent initialized with public key: {nostr_agent.public_key.bech32()}")

Next Steps
----------

- **Run Your Agent**: Learn how to run an agent with `NostrAgentServer` in the :doc:`../getting_started/simple_agent` guide.
- **Enable Payments**: Add payment processing to your agent in the :doc:`../getting_started/payment_enabled_agent` guide.
- **Discoverability**: Enhance your agent's visibility with metadata in the :doc:`../key_concepts/nostr_metadata` guide.

Reference
---------

.. automodule:: agentstr.agents.nostr_agent
   :members:
   :undoc-members:
   :show-inheritance:
