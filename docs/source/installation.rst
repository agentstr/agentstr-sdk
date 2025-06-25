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

Install the core SDK and CLI only:

.. code-block:: bash

   uv add agentstr-sdk[cli]       # or: pip install "agentstr-sdk[cli]"

All-in-One Install
------------------

To include **all** optional extras (CLI, RAG, AI back-ends, …):

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

Optional Extras
---------------

You can install Agentstr SDK with additional features by specifying one or more "extras" in your pip/uv install command. Each extra enables support for specific integrations or capabilities:

.. list-table:: Available Extras
   :header-rows: 1

   * - Extra
     - Description
     - Included Packages
   * - ``cli``
     - CLI and cloud deployment support
     - click, boto3, google-cloud-run, azure-mgmt-containerinstance, azure-identity, PyYAML, nostr-relay
   * - ``rag``
     - Retrieval-Augmented Generation (RAG) support
     - langchain, langchain-community, langchain-openai
   * - ``langgraph``
     - LangGraph integration
     - langchain-openai, langgraph
   * - ``dspy``
     - DeepSpeed/LLM pipeline integration
     - dspy, langchain-openai
   * - ``agno``
     - Agno integration
     - langchain-openai, agno
   * - ``pydantic``
     - Pydantic AI model helpers
     - pydantic-ai-slim[openai]
   * - ``openai``
     - OpenAI Agents integration
     - openai-agents
   * - ``google``
     - Google ADK and LiteLLM integration
     - google-adk, litellm
   * - ``examples``
     - Extra dependencies for running example scripts
     - yfinance, python-dotenv
   * - ``all``
     - Installs all optional dependencies above
     - All of the above packages

To install with one or more extras, use:

.. code-block:: bash

   uv add agentstr-sdk[EXTRA1,EXTRA2,...]   # or: pip install "agentstr-sdk[EXTRA1,EXTRA2,...]"

Replace ``EXTRA1,EXTRA2,...`` with any combination from the table above. For example:

.. code-block:: bash

   uv add agentstr-sdk[rag,openai]   # or: pip install "agentstr-sdk[rag,openai]"

