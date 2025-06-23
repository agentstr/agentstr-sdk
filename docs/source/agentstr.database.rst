Database Abstraction
====================

The ``agentstr.database`` package provides a database abstraction layer with SQLite and Postgres implementations. It is organized as a package with the following submodules:

- ``agentstr.database.base``: Abstract base classes and models
- ``agentstr.database.sqlite``: SQLite backend implementation
- ``agentstr.database.postgres``: Postgres backend implementation

The package offers a simple factory that selects the appropriate backend based on the connection string and exposes a consistent asynchronous API for CRUD operations and thread management.

.. toctree::
   :maxdepth: 1
   :caption: Database API

   agentstr.database.base
   agentstr.database.sqlite
   agentstr.database.postgres

.. automodule:: agentstr.database
   :members:
   :undoc-members:
   :show-inheritance:
