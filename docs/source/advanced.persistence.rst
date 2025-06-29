Persistence
===========

`agentstr` supports persistence for storing user data and message history. This is handled by the :class:`~agentstr.database.database.Database` class, which provides an abstraction over different database backends.

**Supported Backends:**

*   **SQLite**: The default, file-based database.
*   **Postgres**: For production environments, via `asyncpg`.

**Message History**

The :class:`~agentstr.database.message_history.MessageHistory` class provides an interface for storing and retrieving conversation histories, which is essential for context-aware agents.
