Data Models
===========

.. _models:

Overview
--------

This module contains the data models used within the Agentstr SDK for handling various data structures and interactions.

High-Level Overview
~~~~~~~~~~~~~~~~~~~

- :class:`~agentstr.models.NoteFilters`: Defines filters for notes, allowing customization of content retrieval based on specific criteria.
- :class:`~agentstr.models.Skill`: Represents a specific capability or skill that an agent can possess or utilize.
- :class:`~agentstr.models.AgentCard`: Provides a summary or profile card for an agent, including key identifying information.
- :class:`~agentstr.models.User`: Models user data, capturing essential information about individuals interacting with the system.
- :class:`~agentstr.models.Message`: Encapsulates communication data between agents and users, including content and metadata.
- :class:`~agentstr.models.ChatInput`: Structures input data for chat interactions, formatting user or system prompts.
- :class:`~agentstr.models.ChatOutput`: Represents the output or response from a chat interaction, including generated content and tool calls.

Reference
---------

.. autopydantic_model:: agentstr.models.NoteFilters

.. autopydantic_model:: agentstr.models.Skill

.. autopydantic_model:: agentstr.models.AgentCard

.. autopydantic_model:: agentstr.models.User

.. autopydantic_model:: agentstr.models.Message

.. autopydantic_model:: agentstr.models.ChatInput

.. autopydantic_model:: agentstr.models.ChatOutput

See Also
--------

- :doc:`agents/nostr_agent` — The nostr agent uses these models for configuration.
- :doc:`database/base` — The database layer uses these models for persisting user data and chat history.
