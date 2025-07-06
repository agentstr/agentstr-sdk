Agentstr Cookbook
=================

Welcome to the Agentstr Cookbook! This section provides practical, real-world examples that showcase the power and flexibility of the Agentstr SDK. Here, you'll find detailed use cases demonstrating how to leverage advanced features to build sophisticated, decentralized applications.

The examples are organized into two main categories: **Agent Examples** and **MCP Server Examples**. Each category includes hands-on projects with source code available in the `cookbook/` directory of the `Agentstr SDK repository <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook>`_.

.. note::
   These cookbook examples are designed to be starting points. Feel free to adapt and extend them to suit your specific needs.

Agent Examples
--------------

Explore how to build agents that interact with users and perform complex tasks. These examples are located in `cookbook/agents/ <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents>`_:

*   **Finance Agent**: An agent that fetches and analyzes stock prices. Dive into the `Finance example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/finance>`_ to see how to integrate financial data APIs.
*   **Travel Planner**: An agent that assists in planning trips, including flights and itineraries. Check out the `Travel example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/travel>`_ for inspiration on user interaction flows.
*   **Nostr RAG**: An agent that performs Retrieval-Augmented Generation (RAG) over Nostr notes. Explore the `Nostr RAG example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/agents/nostr_rag>`_ to learn about advanced data retrieval techniques.

MCP Server Examples
-------------------

Learn how to create Model Context Protocol (MCP) servers that provide specialized tools for agents. These examples are located in `cookbook/mcp_servers/ <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/mcp_servers>`_:

*   **Web Search Server**: An MCP server that enables web search capabilities for agents. See the `Web Search example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/mcp_servers/web_search>`_ to understand how to integrate search functionality.
*   **Bitcoin Data Server**: An MCP server for fetching Bitcoin-related data. Review the `Bitcoin example <https://github.com/agentstr/agentstr-sdk/tree/main/cookbook/mcp_servers/bitcoin>`_ to learn about blockchain data integration.

Getting Started with Examples
-----------------------------

To try out these examples:

1. **Clone the Repository**: If you haven't already, clone the `Agentstr SDK repo <https://github.com/agentstr/agentstr-sdk>`_.
2. **Navigate to Cookbook**: Go to the `cookbook/` directory to find the example folders.
3. **Follow READMEs**: Each example includes a `README.md` with setup and running instructions.

.. tip::
   Start with simpler examples like the Finance Agent or Web Search Server to get familiar with the structure before moving to more complex ones like Nostr RAG.

By studying and experimenting with these examples, you'll gain insights into combining different providers and MCPs to build powerful, decentralized applications tailored to your needs.

Next Steps
----------

*   **Contribute**: Have an interesting use case? Contribute to the cookbook by submitting a pull request to the `Agentstr SDK project <https://github.com/agentstr/agentstr-sdk>`_.
*   **Explore API**: Deepen your understanding by exploring the :doc:`Core Modules <agentstr>` documentation.
*   **Deploy**: Ready to take your application live? Check out the :doc:`Cloud CI/CD <cloud_cicd>` guide for deployment strategies.
