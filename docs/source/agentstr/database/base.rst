Database Interface
==================

This module defines the abstract interface and shared data models for all database backends in Agentstr. It provides a common interface that all database implementations must adhere to.

Overview
--------

The central component is the ``BaseDatabase`` abstract base class, which outlines the required methods for any database backend, such as connecting, disconnecting, and performing CRUD operations on Nostr-related data. This ensures that different backends can be used interchangeably.

**Key Components:**

- ``BaseDatabase``: The abstract base class for all database implementations.
- Shared Pydantic models for data consistency across backends.

Reference
---------

.. automodule:: agentstr.database.base
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------
- :doc:`sqlite` — for the SQLite implementation.
- :doc:`postgres` — for the PostgreSQL implementation.
