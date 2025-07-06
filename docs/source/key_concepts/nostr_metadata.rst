Nostr Metadata
==============

This document explains the `Metadata` class from the `pynostr` library, which is used to define profile information for entities on the Nostr network, such as agents or MCP servers.

Overview of Metadata
--------------------

The `Metadata` class is a specialized type of `Event` in the Nostr protocol that allows you to set profile information for a public key. This information is broadcast to the network and can be discovered by other users or services.

The class is defined as follows:

.. code-block:: python

   from dataclasses import dataclass
   from pynostr.event import Event
   from typing import Optional

   @dataclass
   class Metadata(Event):
       name: Optional[str] = None
       about: Optional[str] = None
       nip05: Optional[str] = None
       picture: Optional[str] = None
       banner: Optional[str] = None
       lud16: Optional[str] = None
       lud06: Optional[str] = None
       username: Optional[str] = None
       display_name: Optional[str] = None
       website: Optional[str] = None

Each field is optional and represents a piece of profile information:

- **name**: A short name or handle for the entity.
- **about**: A brief description or bio.
- **nip05**: An identifier for NIP-05 verification (DNS-based identity).
- **picture**: URL to a profile picture or avatar.
- **banner**: URL to a banner image.
- **lud16**: Lightning address for receiving payments (human-readable).
- **lud06**: Lightning address for receiving payments (LNURL).
- **username**: Alternative short identifier.
- **display_name**: A longer or formatted name for display purposes.
- **website**: URL to a personal or project website.

Using Metadata with Agentstr
----------------------------

In the Agentstr SDK, you can pass an instance of `Metadata` to both the `NostrAgent` and `NostrMCPServer` classes. When provided, the SDK will automatically update and broadcast this metadata on the Nostr network, allowing other users to discover and interact with your agent or MCP server using the provided profile information.

Example with NostrAgent
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pynostr.metadata import Metadata
   from agentstr import NostrAgent, AgentCard

   # Define metadata for the agent
   agent_metadata = Metadata(
       name="MyAgent",
       about="A helpful AI agent built with Agentstr.",
       picture="https://example.com/my-agent-picture.png",
       lud16="myagent@lnaddress.com"
   )

   # Initialize the agent with metadata
   agent_card = AgentCard(name="MyAgent", description="A helpful AI agent")
   nostr_agent = NostrAgent(
       agent_card=agent_card,
       nostr_metadata=agent_metadata,
       chat_generator=your_chat_function
   )

Example with NostrMCPServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pynostr.metadata import Metadata
   from agentstr import NostrMCPServer

   # Define metadata for the MCP server
   server_metadata = Metadata(
       name="MathToolsServer",
       about="An MCP server providing mathematical tools.",
       picture="https://example.com/math-tools-icon.png",
       website="https://mathtools.example.com"
   )

   # Initialize the MCP server with metadata
   server = NostrMCPServer(
       name="Math Tools MCP Server",
       relays=["wss://relay.example.com"],
       private_key="your-private-key",
       nostr_metadata=server_metadata,
       tools=[add, multiply]
   )

Benefits
--------

- **Discoverability**: Metadata makes your agent or MCP server more discoverable on the Nostr network by providing descriptive information.
- **User Trust**: Including verification details (like NIP-05) or payment addresses (like lud16) can build trust with users.
- **Branding**: Use profile pictures, banners, and display names to create a consistent identity for your services.

Next Steps
----------

- **Explore Agent Customization**: Learn more about building agents in the :doc:`../getting_started/simple_agent` guide.
- **Create MCP Tools**: See the :doc:`../getting_started/creating_an_mcp_server` guide for creating tools with MCP servers.
