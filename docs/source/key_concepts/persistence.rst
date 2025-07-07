Persistence
===========

Agentstr supports persistence for storing user data and message history. This is handled by the :class:`~agentstr.database.database.Database` class, which provides an abstraction over different database backends.

These features are enabled by default for all Agentstr agents.

Environments
------------

When running Agentstr SDK locally, SQLite is used by default. For production environments, Postgres is recommended and can be configured automatically in the configuration file when running **agentstr deploy**.

Check out :doc:`../../cloud_cicd` for more information on how to deploy your Agentstr agent to the cloud.

**Supported Backends:**

*   **SQLite**: The default, file-based database, via `aiosqlite`.
*   **Postgres**: For production environments, via `asyncpg`.

**Message History**

The :class:`~agentstr.models.Message` class provides an interface for storing and retrieving conversation histories, which is essential for context-aware agents.

For more information on database configurations and advanced persistence options, refer to :doc:`../../agentstr.database`.

Relevant Modules
----------------

*   :doc:`../../agentstr.database`
*   :class:`~agentstr.models.Message`
