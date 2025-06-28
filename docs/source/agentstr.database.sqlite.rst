SQLite Database Backend
=======================

This module provides the SQLite implementation of the ``NostrDB`` interface. It is a lightweight, file-based database backend that is suitable for local development and testing.

Overview
--------

The ``SQLiteNostrDB`` class can be used to create a database connection to a local SQLite file.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.database.sqlite import SQLiteNostrDB

   # Create a database instance
   db = SQLiteNostrDB(database_path=":memory:")

   async def main():
       await db.connect()
       # ... perform database operations
       await db.disconnect()

   asyncio.run(main())

Reference
---------

.. automodule:: agentstr.database.sqlite
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`agentstr.database.base` — for the abstract base class.
- :doc:`agentstr.database.postgres` — for the PostgreSQL implementation.
