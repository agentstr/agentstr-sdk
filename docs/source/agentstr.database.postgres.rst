Postgres Database Backend
=========================

This module provides the PostgreSQL implementation of the ``NostrDB`` interface. It is a robust, production-ready database backend.

Overview
--------

The ``PostgresNostrDB`` class can be used to create a database connection to a PostgreSQL server.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.database.postgres import PostgresNostrDB

   # Create a database instance
   db = PostgresNostrDB(database_url="postgresql+asyncpg://user:password@host/dbname")

   async def main():
       await db.connect()
       # ... perform database operations
       await db.disconnect()

   asyncio.run(main())

Reference
---------

.. automodule:: agentstr.database.postgres
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.database.base` — for the abstract base class.
- :doc:`agentstr.database.sqlite` — for the SQLite implementation.
