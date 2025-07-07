Data Models
===========

.. _models:

Overview
--------

This module defines the core Pydantic data models that are shared across the Agentstr SDK. These models provide type-safe schemas for agent capabilities, messages, and other structured data exchanged throughout the system.

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

- :doc:`agentstr.cli` — The command-line interface uses these models for configuration.
- :doc:`agentstr.database.base` — The database layer uses these models for storage.
