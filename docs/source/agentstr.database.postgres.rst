Postgres Database Backend
=========================

This module provides the PostgreSQL implementation of the ``BaseDatabase`` interface. It is a robust, production-ready database backend.

Overview
--------

The ``PostgresDatabase`` class can be used to create a database connection to a PostgreSQL server.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.database.postgres import PostgresDatabase

   # Note: To run this example, you need a running PostgreSQL server
   # and the 'asyncpg' driver installed.
   # pip install asyncpg

   # Create a database instance with the connection string
   db = PostgresDatabase(conn_str="postgresql://user:password@host/dbname")

   async def main():
       await db.async_init()
       print("Connection to PostgreSQL successful.")
       # ... perform database operations
       await db.close()
       print("Connection closed.")

   # To run this, you would typically use:
   # if __name__ == "__main__":
   #     asyncio.run(main())

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
