Installation
============

Agentstr SDK is distributed on PyPI and supports **Python 3.12**.
The package bundles optional extras so you can install just the
functionality you need.

Prerequisites
-------------

* Python 3.12 or newer
* [uv](https://docs.astral.sh/uv/) (recommended) **or** `pip`

Basic Install
-------------

Install the core SDK only:

.. code-block:: bash

   uv add agentstr-sdk            # or: pip install agentstr-sdk

All-in-One Install
------------------

To include **all** optional extras (CLI, RAG, MCP back-ends, …):

.. code-block:: bash

   uv add agentstr-sdk[all]       # or: pip install "agentstr-sdk[all]"

Install From Source
-------------------

.. code-block:: bash

   git clone https://github.com/agentstr/agentstr-sdk.git
   cd agentstr-sdk
   uv sync --all-extras           # or: pip install -e .[all]

Verify the installation:

.. code-block:: bash

   agentstr --help      # CLI should print the help text

