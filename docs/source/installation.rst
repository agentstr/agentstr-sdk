Installation
============

The Agentstr SDK is available on PyPI and requires Python 3.12 or newer.

.. tip::
   We recommend using `uv <https://docs.astral.sh/uv/>`_ for faster dependency management, but ``pip`` is also supported.

Standard Installation
---------------------

To get started with the core SDK and command-line interface (CLI), run:

.. code-block:: bash

   uv add agentstr-sdk[cli]
   # Or with pip:
   # pip install "agentstr-sdk[cli]"

Full Installation
-----------------

To install the SDK with all optional features, including AI integrations and example dependencies, use the ``[all]`` extra:

.. code-block:: bash

   uv add agentstr-sdk[all]
   # Or with pip:
   # pip install "agentstr-sdk[all]"

Custom Installation
-------------------

You can also install specific extras to tailor the SDK to your needs. Here are the available options:

.. list-table:: Optional Extras
   :header-rows: 1
   :widths: 15 50

   * - Extra
     - Description
   * - ``rag``
     - Adds support for Retrieval-Augmented Generation (RAG).
   * - ``langgraph``
     - Integrates with LangGraph for building stateful, agentic applications.
   * - ``dspy``
     - Provides tools for working with DSPy.
   * - ``agno``
     - Integrates with Agno for building and evaluating AI agents.
   * - ``pydantic``
     - Includes helpers for using Pydantic's AI framework.
   * - ``openai``
     - Adds support for OpenAI's agent ecosystem.
   * - ``google``
     - Integrates with Google's AI developer kits.

To install one or more extras, list them in your installation command:

.. code-block:: bash

   uv add agentstr-sdk[rag,openai]
   # Or with pip:
   # pip install "agentstr-sdk[rag,openai]"

Installation from Source
------------------------

If you want to work with the latest development version, you can install the SDK from source:

.. code-block:: bash

   git clone https://github.com/agentstr/agentstr-sdk.git
   cd agentstr-sdk
   uv pip install -e .[all]
   # Or with pip:
   # pip install -e .[all]

After installation, you can verify that everything is working by running:

.. code-block:: bash

   agentstr --help

This should display the CLI help menu, confirming that the SDK is ready to use.
