SQLite Database Backend
=======================

This module provides the SQLite implementation of the ``BaseDatabase`` interface. It is a lightweight, file-based database backend that is suitable for local development and testing.

Overview
--------

The ``SQLiteDatabase`` class can be used to create a database connection to a local SQLite file.

**Typical usage:**

.. code-block:: python

   import asyncio
   from agentstr.database.sqlite import SQLiteDatabase

   # Create a database instance for an in-memory database
   db = SQLiteDatabase(conn_str="sqlite://:memory:")

   async def main():
       await db.async_init()
       print("Connection to SQLite successful.")
       # ... perform database operations
       await db.close()
       print("Connection closed.")

   # To run this, you would typically use:
   # if __name__ == "__main__":
   #     asyncio.run(main())

Reference
---------

.. automodule:: agentstr.database.sqlite
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`base` — for the abstract base class.
- :doc:`postgres` — for the PostgreSQL implementation.
